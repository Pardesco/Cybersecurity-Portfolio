import sys
import argparse
import os
from analyzer import analyze_wallet
from reporter import generate_report

def main():
    parser = argparse.ArgumentParser(description="Crypto Incident Response MVP Tool")
    parser.add_argument("wallet", help="Ethereum wallet address to analyze")
    args = parser.parse_args()

    wallet_address = args.wallet
    
    # Basic validation of Ethereum address
    if not wallet_address.startswith("0x") or len(wallet_address) != 42:
        print("[-] Error: Invalid Ethereum address format. Must be 42 characters and start with '0x'.")
        sys.exit(1)
        
    print(f"[*] Starting Incident Response Analysis for wallet: {wallet_address}")
    
    try:
        report = analyze_wallet(wallet_address)
        generate_report(report)
    except Exception as e:
        print(f"[-] An error occurred during analysis: {e}")

if __name__ == "__main__":
    main()
