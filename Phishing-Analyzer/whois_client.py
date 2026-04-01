import whois
from urllib.parse import urlparse
import datetime

def get_domain_age_days(url):
    """Performs a WHOIS lookup to calculate domain age in days."""
    try:
        domain = urlparse(url).netloc
        if not domain:
            return None
        
        # Remove port if present
        if ":" in domain:
            domain = domain.split(":")[0]
            
        w = whois.whois(domain)
        creation_date = w.creation_date
        
        # WHOIS can sometimes return a list of dates
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
            
        if not creation_date:
            return None
            
        age = datetime.datetime.now() - creation_date
        return max(age.days, 0)
    except Exception as e:
        # WHOIS might fail or domain doesn't exist
        return None
