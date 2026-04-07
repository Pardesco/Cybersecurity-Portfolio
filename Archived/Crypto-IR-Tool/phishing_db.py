import requests
import json

METAMASK_PHISHING_URL = "https://raw.githubusercontent.com/MetaMask/eth-phishing-detect/master/src/config.json"

class PhishingDB:
    def __init__(self):
        self.blocked_domains = []
        self.fuzzers = []
        self._load_db()

    def _load_db(self):
        """Loads the official MetaMask eth-phishing-detect list."""
        print("[*] Fetching MetaMask phishing detection list...")
        try:
            response = requests.get(METAMASK_PHISHING_URL)
            response.raise_for_status()
            data = response.json()
            self.blocked_domains = data.get("blacklist", [])
            self.fuzzers = data.get("fuzzers", [])
        except Exception as e:
            print(f"[!] Warning: Could not load MetaMask phishing list: {e}")

    def is_flagged(self, string_to_check):
        """
        Checks if a domain or associated string is in the blacklist.
        Note: The MetaMask list is predominantly domain-based, but we can 
        use it as a baseline Threat Intel feed for cross-referencing.
        """
        string_to_check = string_to_check.lower()
        if string_to_check in self.blocked_domains:
            return True
        for fuzzer in self.fuzzers:
            if fuzzer in string_to_check:
                return True
        return False
