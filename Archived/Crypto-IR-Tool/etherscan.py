import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
BASE_URL = "https://api.etherscan.io/api"

def get_transactions(address, limit=200):
    """Fetches normal transactions for a given address."""
    if not ETHERSCAN_API_KEY or ETHERSCAN_API_KEY == "your_etherscan_api_key_here":
        raise ValueError("Missing valid ETHERSCAN_API_KEY in .env file")
        
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": limit,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    
    if data.get("status") == "1":
        return data.get("result", [])
    else:
        print(f"[-] Etherscan API Error (Normal Txs): {data.get('message')}")
        return []

def get_erc20_transfers(address, limit=200):
    """Fetches ERC20 token transfers for a given address."""
    params = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": limit,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    
    if data.get("status") == "1":
        return data.get("result", [])
    else:
        print(f"[-] Etherscan API Error (ERC20 Txs): {data.get('message')}")
        return []

def get_contract_abi(address):
    """
    Checks if a contract source code is verified on Etherscan by requesting its ABI.
    Returns True if verified, False otherwise.
    """
    params = {
        "module": "contract",
        "action": "getabi",
        "address": address,
        "apikey": ETHERSCAN_API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    return data.get("status") == "1"
