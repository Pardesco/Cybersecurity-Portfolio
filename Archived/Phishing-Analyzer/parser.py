import email
from email import policy
import re

def parse_eml(file_path):
    """Parses a raw .eml file and extracts relevant headers and URLs."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        msg = email.message_from_file(f, policy=policy.default)
        
    extracted_data = {
        "from": msg.get("From", ""),
        "reply_to": msg.get("Reply-To", ""),
        "to": msg.get("To", ""),
        "subject": msg.get("Subject", ""),
        "date": msg.get("Date", ""),
        "authentication_results": msg.get("Authentication-Results", ""),
        "received_ips": [],
        "urls": []
    }
    
    # Extract Received IPs (basic regex for IPv4)
    received_headers = msg.get_all("Received")
    if received_headers:
        for header in received_headers:
            ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', header)
            for ip in ips:
                if ip not in extracted_data["received_ips"] and not ip.startswith("127.") and not ip.startswith("10.") and not ip.startswith("192.168."):
                    extracted_data["received_ips"].append(ip)
                    
    # Extract Body to find URLs
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
            if ctype in ['text/plain', 'text/html'] and 'attachment' not in cdispo:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode(errors='ignore')
                except Exception:
                    pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(errors='ignore')
        except Exception:
            pass
            
    # Extract URLs
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', body)
    
    # Clean trailing punctuation from URLs
    clean_urls = []
    for u in urls:
        clean_url = u.rstrip("'\".<>)]}")
        if clean_url not in clean_urls:
            clean_urls.append(clean_url)
            
    extracted_data["urls"] = clean_urls
    
    return extracted_data
