import whois
from datetime import datetime
import time

def clean_domain_name(domain_name):
    """
    Clean the domain name by:
    1. Removing spaces
    2. Converting to lowercase
    3. Removing any special characters
    """
    return domain_name.strip().replace(" ", "").lower()

def append_to_file(domain, filename):
    """
    Append a domain to the specified file
    """
    with open(filename, 'a') as f:
        f.write(f"{domain[:-4]}\n")

def check_single_domain(domain_name):
    """
    Check the availability of a single .com domain.
    Returns the availability status.
    """
    cleaned_domain = clean_domain_name(domain_name)
    domain = f"{cleaned_domain}.com"
    
    try:
        # Add a small delay to avoid hitting rate limits
        time.sleep(1)
        
        # Try to get domain information
        domain_info = whois.whois(domain)
        
        # Check if the domain is registered
        if domain_info.domain_name is None:
            append_to_file(domain, 'available.txt')
            return "Available"
        else:
            # If expiration date exists, check if it's expired
            if isinstance(domain_info.expiration_date, list):
                expiration_date = domain_info.expiration_date[0]
            else:
                expiration_date = domain_info.expiration_date
            
            if expiration_date and expiration_date > datetime.now():
                append_to_file(domain, 'notAvailable.txt')
                return "Not Available"
            else:
                append_to_file(domain, 'available.txt')
                return "Available"
                
    except whois.parser.PywhoisError:
        # If we get a PywhoisError, the domain might be available
        append_to_file(domain, 'available.txt')
        return "Available"
    except Exception as e:
        return f"Error checking domain: {str(e)}"

def process_domains_from_file(filename):
    """
    Read domains from a file and check availability one by one,
    printing results immediately.
    """
    try:
        with open(filename, 'r') as file:
            print("Starting domain availability check...")
            print("-" * 70)
            print(f"{'Original Domain':<30} {'Cleaned Domain':<30} {'Status'}")
            print("-" * 70)
            
            for line in file:
                original_domain = line.strip()
                if original_domain:  # Skip empty lines
                    cleaned_domain = clean_domain_name(original_domain)
                    status = check_single_domain(cleaned_domain)
                    print(f"{original_domain:<30} {cleaned_domain + '.com':<30} {status}")
    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error reading file: {str(e)}")

def main():
    filename = 'try.txt'
    process_domains_from_file(filename)
    print("\nDomains have been appended to 'available.txt' and 'notAvailable.txt'")

if __name__ == "__main__":
    main()