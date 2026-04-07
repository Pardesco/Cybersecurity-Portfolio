import sys
import os

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_analyzer import analyze_wallet
from reporter import generate_report

def run_test():
    """
    Runs the IR tool against a known active wallet to demonstrate 
    functionality without requiring a real live incident.
    (Using an exchange hot wallet or heavily active address for data volume)
    """
    # Example: A highly active Binance hot wallet address to guarantee transaction data
    test_wallet = "0x28C6c06298d514Db089934071355E22Af1614009"
    
    print(f"--- Running Test Simulation on Address: {test_wallet} ---")
    try:
        report = analyze_wallet(test_wallet)
        generate_report(report)
    except ValueError as e:
        print(f"\n[!] Test Failed: {e}")
        print("[!] Please ensure you have added an Etherscan API key to the .env file in the root of Crypto-IR-Tool.")

if __name__ == "__main__":
    run_test()
