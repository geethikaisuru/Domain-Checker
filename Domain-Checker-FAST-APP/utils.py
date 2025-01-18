# utils.py
import whois
from datetime import datetime

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
