import streamlit as st
import whois
from datetime import datetime
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import threading

# Page configuration
st.set_page_config(
    page_title="Domain Checker Pro",
    page_icon="\U0001F50D"
)

# CSS styles
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1E88E5;
        padding: 20px;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f0f2f6;
        padding: 10px 0;
        text-align: center;
        z-index: 999;
    }
    .social-links {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        margin-bottom: 10px;
    }
    .social-links a {
        text-decoration: none;
        color: #1E88E5;
        display: inline-flex;
        align-items: center;
    }
    .main {
        padding-bottom: 100px;
    }
    </style>
    """, unsafe_allow_html=True)

def clean_domain_name(domain_name: str) -> str:
    """Clean the domain name"""
    return domain_name.strip().replace(" ", "").lower()

def check_single_domain(domain_name: str) -> tuple[str, str]:
    """Check a single domain with minimal delay"""
    cleaned_domain = clean_domain_name(domain_name)
    domain = f"{cleaned_domain}.com"

    try:
        domain_info = whois.whois(domain)

        if domain_info.domain_name is None:
            return "Available ✅", None
        else:
            expiration_date = domain_info.expiration_date
            if isinstance(expiration_date, list):
                expiration_date = expiration_date[0]

            if expiration_date and expiration_date > datetime.now():
                return "Not Available ❌", None
            else:
                return "Available ✅", None

    except whois.parser.PywhoisError:
        return "Available ✅", None
    except Exception as e:
        return "Error ⚠️", str(e)

class DomainChecker:
    def __init__(self, max_workers: int = 10, rate_limit: float = 0.1):
        self.max_workers = max_workers
        self.rate_limit = rate_limit
        self.results_queue = queue.Queue()
        self.worker_progress = {i: 0.0 for i in range(max_workers)}
        self.processed_count = 0
        self.total_domains = 0
        self.last_request_time = time.time()
        self.lock = threading.Lock()

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
            self.processed_count += 1
            self.worker_progress[worker_id] = self.processed_count / worker_domains
            self.results_queue.put((result, self.processed_count / self.total_domains, worker_id))

        return result

    def check_domains(self, domains: list, progress_bars: dict) -> list:
        """Check multiple domains in parallel with working progress bars"""
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
                    st.error(f"Error processing domain: {str(e)}")

        return results

def process_domain_list(domains: list) -> list:
    """Process a list of domains with working progress tracking"""
    if not domains:
        return []

    main_progress = st.progress(0.0, "Overall Progress")
    worker_progress_bars = {
        i: st.progress(0.0, f"Worker {i+1} Progress")
        for i in range(10)
    }
    status_text = st.empty()
    results_container = st.empty()

    checker = DomainChecker(max_workers=10, rate_limit=0.1)
    results_df = pd.DataFrame(columns=['Original Domain', 'Cleaned Domain', 'Status', 'Error'])

    def update_progress():
        results = []
        while len(results) < len(domains):
            try:
                result, overall_progress, worker_id = checker.results_queue.get(timeout=0.1)
                results.append(result)

                main_progress.progress(overall_progress)
                worker_progress_bars[worker_id].progress(checker.worker_progress[worker_id])

                status_text.text(f"\U0001F50D Processed {len(results)}/{len(domains)} domains")

                results_df.loc[len(results_df)] = result
                results_container.dataframe(results_df)

            except queue.Empty:
                continue
            except Exception as e:
                st.error(f"Error in progress update: {str(e)}")
                break

        return results

    progress_thread = threading.Thread(target=update_progress)
    progress_thread.start()

    results = checker.check_domains(
        [d for d in domains if d.strip()],
        worker_progress_bars
    )

    progress_thread.join()

    time.sleep(1)
    for progress_bar in worker_progress_bars.values():
        progress_bar.empty()

    return results

def main():
    st.markdown('<div class="main">', unsafe_allow_html=True)

    st.markdown("<h1 class='main-title'>\U0001F50D Domain Availability Checker Pro</h1>", unsafe_allow_html=True)
    st.markdown("### Find your perfect domain name! \U0001F3AF")

    tab1, tab2 = st.tabs(["\U0001F4D1 Bulk Domain Check", "\U0001F3AF Single Domain Check"])

    with tab1:
        st.header("\U0001F4D1 Bulk Domain Check")

        input_method = st.radio(
            "Choose input method",
            ["Upload TXT File \U0001F4C2", "Paste Domain List \U0001F4DD"]
        )

        domains = None

        if input_method == "Upload TXT File \U0001F4C2":
            st.info("Upload a text file with one domain name per line")
            uploaded_file = st.file_uploader("Choose a file", type=['txt'])

            if uploaded_file is not None:
                domains = [line.decode('utf-8').strip() for line in uploaded_file]

        else:
            st.info("Enter domain names (one per line)")
            text_input = st.text_area(
                "Paste your domains here",
                height=200,
                placeholder="example1\nexample2\nexample3"
            )

            if text_input:
                domains = [line.strip() for line in text_input.split('\n')]

        if domains:
            if st.button("\U0001F680 Check All Domains"):
                results = process_domain_list(domains)

                df = pd.DataFrame(results)
                st.success("\u2728 Check completed!")
                st.dataframe(df)

                csv = df.to_csv(index=False)
                st.download_button(
                    label="\U0001F4E5 Download Results as CSV",
                    data=csv,
                    file_name="domain_check_results.csv",
                    mime="text/csv"
                )

    with tab2:
        st.header("\U0001F3AF Single Domain Check")
        st.info("Quick check for a single domain name")
        domain_name = st.text_input("Enter domain name (without .com) \U0001F310:")

        if st.button("\U0001F50D Check Availability"):
            if domain_name:
                with st.spinner('\U0001F504 Checking domain availability...'):
                    status, error = check_single_domain(domain_name)

                    if error:
                        st.error(f"\u26A0\uFE0F Error checking domain: {error}")
                    else:
                        if "Available" in status:
                            st.success(f"\U0001F389 Domain {domain_name}.com is Available!")
                            st.balloons()
                        else:
                            st.warning(f"\U0001F614 Domain {domain_name}.com is Not Available")
            else:
                st.warning("\u26A0\uFE0F Please enter a domain name")

    st.markdown("""
        <div class='footer'>
            <div class='social-links'>
                <a href='https://www.linkedin.com/in/geethikaisuru/' target='_blank'>\U0001F517 LinkedIn</a>
                <a href='https://github.com/geethikaisuru' target='_blank'>\U0001F4BB GitHub</a>
            </div>
            <p>Built with \u2764\uFE0F by Geethika</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
