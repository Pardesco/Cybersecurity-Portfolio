import json
import time
import os

def generate_report(report_data):
    """Outputs the report as structured JSON and prints a console summary."""
    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)
    
    timestamp = int(time.time())
    wallet = report_data["wallet_address"]
    filepath = f"reports/{wallet}-{timestamp}.json"
    
    # Write structured JSON
    with open(filepath, "w") as f:
        json.dump(report_data, f, indent=4)
        
    # Print Console Summary
    print(f"\n[+] Analysis Complete. JSON Report saved to: {filepath}\n")
    print("="*60)
    print(f"INCIDENT SUMMARY FOR: {wallet}")
    print("="*60)
    print(f"Total Transactions Analyzed: {report_data['total_txs_analyzed']}")
    print(f"Estimated Attack Type:       {report_data['attack_type']}")
    print(f"Suspicious Approvals Found:  {len(report_data['suspicious_approvals'])}")
    print(f"Total ETH Transferred Out:   {report_data['value_transferred_out_eth']:.6f} ETH\n")
    
    if report_data["suspicious_approvals"]:
        print("[!] SUSPICIOUS CONTRACTS FLAGGED:")
        for app in report_data["suspicious_approvals"]:
            print(f"    - Contract: {app['contract']}")
            print(f"      Reason:   {app['reason']}")
            print(f"      Tx Hash:  {app['tx_hash'][:15]}...\n")
            
    print("[!] PRIORITIZED ACTION STEPS:")
    if "Approval Exploit" in report_data["attack_type"] or "Pending Attack" in report_data["attack_type"]:
        print("    1. IMMEDIATE ACTION: Go to Revoke.cash or Etherscan Token Approval Checker.")
        print("    2. Revoke the malicious token approvals listed above to prevent further draining.")
        print("    3. Move any remaining valuable tokens to a fresh, secure cold wallet.")
    elif "Seed" in report_data["attack_type"]:
        print("    1. DO NOT deposit further funds (e.g., ETH for gas) to attempt rescue.")
        print("    2. Sweeper bots are likely active on this address and will steal gas deposits.")
        print("    3. Abandon this wallet completely. Generate a new seed phrase on a clean device.")
    else:
        print("    1. No immediate automated drain or malicious approvals detected.")
        print("    2. Continue monitoring transaction history.")
    print("="*60)
