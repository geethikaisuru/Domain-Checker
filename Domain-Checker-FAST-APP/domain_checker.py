import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import clean_domain_name, check_single_domain
import streamlit as st

class DomainChecker:
    def __init__(self, max_workers: int = 10, rate_limit: float = 0.1):
        self.max_workers = max_workers
        self.rate_limit = rate_limit
        self.results_queue = queue.Queue()
        self.worker_progress = {i: 0.0 for i in range(max_workers)}
        self.worker_processed_count = {i: 0 for i in range(max_workers)}  # Added
        self.processed_count = 0
        self.total_domains = 0
        self.last_request_time = time.time()
        self.lock = threading.Lock()
        self.progress_bars = [st.progress(0.0) for _ in range(max_workers)]  # Added

    def process_domain(self, domain: str, worker_id: int, worker_domains: int) -> dict:
        """Process a single domain with rate limiting and worker-specific progress"""
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.rate_limit:
                time.sleep(self.rate_limit - time_since_last)
            self.last_request_time = time.time()

        status, error = check_single_domain(domain)

        result = {
            'Original Domain': domain,
            'Cleaned Domain': f"{clean_domain_name(domain)}.com",
            'Status': status,
            'Error': error if error else '',
            'Worker': worker_id
        }

        with self.lock:
            self.worker_processed_count[worker_id] += 1
            self.worker_progress[worker_id] = self.worker_processed_count[worker_id] / worker_domains
            self.processed_count += 1
            self.results_queue.put((result, self.processed_count / self.total_domains, worker_id))
            self.progress_bars[worker_id].progress(self.worker_progress[worker_id])  # Added

        return result

    def check_domains(self, domains: list) -> list:
        """Check multiple domains in parallel"""
        self.processed_count = 0
        self.total_domains = len(domains)
        results = []

        worker_domain_lists = [[] for _ in range(self.max_workers)]
        for i, domain in enumerate(domains):
            if domain.strip():
                worker_domain_lists[i % self.max_workers].append(domain)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for worker_id, worker_domains in enumerate(worker_domain_lists):
                if worker_domains:
                    for domain in worker_domains:
                        futures.append(
                            executor.submit(
                                self.process_domain,
                                domain,
                                worker_id,
                                len(worker_domains)
                            )
                        )

            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    results.append({'Error': f"Error processing domain: {str(e)}"})

        return results