import os
import requests
from dotenv import load_dotenv
import base64

load_dotenv()
VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
VT_API_URL = "https://www.virustotal.com/api/v3"

def check_url(url):
    """Checks a URL against VirusTotal free API."""
    if not VT_API_KEY or VT_API_KEY == "your_virustotal_api_key_here":
        print("[-] Warning: VirusTotal API key not configured in .env. Skipping VT check.")
        return None
    
    # VT requires URL to be base64url encoded without padding
    url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
    headers = {
        "accept": "application/json",
        "x-apikey": VT_API_KEY
    }
    
    try:
        response = requests.get(f"{VT_API_URL}/urls/{url_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
            return stats
        elif response.status_code == 404:
            # URL not found in VT database
            return {"malicious": 0, "suspicious": 0, "undetected": 0, "harmless": 0, "unrated": 1}
        else:
            print(f"[-] VT API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[-] Error querying VirusTotal: {e}")
        return None
