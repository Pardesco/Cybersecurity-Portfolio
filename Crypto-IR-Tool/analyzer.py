import json
from etherscan import get_transactions, get_erc20_transfers, get_contract_abi
from phishing_db import PhishingDB

def analyze_wallet(address):
    """Core logic to analyze the wallet for indicators of compromise."""
    txs = get_transactions(address)
    erc20_txs = get_erc20_transfers(address)
    phishing_db = PhishingDB()
    
    report = {
        "wallet_address": address,
        "total_txs_analyzed": len(txs) + len(erc20_txs),
        "suspicious_approvals": [],
        "value_transferred_out_eth": 0.0,
        "value_transferred_out_tokens_usd_est": 0.0, # Placeholder for token value
        "attack_type": "None Detected",
        "events": []
    }
    
    approvals = []
    outbound_transfers = []
    
    # 1. Analyze Normal Transactions for Approvals and Outbound ETH
    # MethodID 0x095ea7b3 is the signature for 'approve(address,uint256)'
    for tx in txs:
        # Check for approval transactions
        if tx.get("input", "").startswith("0x095ea7b3"):
            # Extract the spender address from the input data (params are 32 bytes, stripped of padding)
            # Input format: 0x095ea7b3 + 32 bytes (address) + 32 bytes (amount)
            raw_address = tx["input"][10:74]
            spender_address = "0x" + raw_address[-40:]
            
            is_verified = get_contract_abi(spender_address)
            is_phishing = phishing_db.is_flagged(spender_address)
            
            approvals.append({
                "hash": tx["hash"],
                "spender_contract": spender_address,
                "verified": is_verified,
                "timestamp": tx["timeStamp"]
            })
            
            # Flag if unverified or explicitly blacklisted
            if not is_verified or is_phishing:
                report["suspicious_approvals"].append({
                    "tx_hash": tx["hash"],
                    "contract": spender_address,
                    "reason": "Unverified Contract / Potential Drainer" if not is_verified else "Flagged in MetaMask DB"
                })

        # Calculate Outbound ETH
        if tx["from"].lower() == address.lower() and int(tx["value"]) > 0:
            outbound_transfers.append(tx)
            report["value_transferred_out_eth"] += int(tx["value"]) / (10**18)
            
    # 2. Analyze ERC20 Transfers (Tokens drained)
    outbound_tokens_count = 0
    for token_tx in erc20_txs:
        if token_tx["from"].lower() == address.lower():
            outbound_tokens_count += 1
            # Real valuation would require a pricing API like CoinGecko. 

    # 3. Determine Attack Type Heuristics
    has_suspicious_approvals = len(report["suspicious_approvals"]) > 0
    has_outbound = report["value_transferred_out_eth"] > 0 or outbound_tokens_count > 0
    
    if has_suspicious_approvals and has_outbound:
        report["attack_type"] = "Approval Exploit (Ice Phishing)"
    elif has_outbound and not has_suspicious_approvals:
        # If funds are leaving rapidly without approvals, it's likely a seed/private key leak
        report["attack_type"] = "Likely Seed/Private Key Compromise"
    elif has_suspicious_approvals and not has_outbound:
        report["attack_type"] = "Pending Attack (Malicious Approvals Active)"

    report["events"] = {
        "total_approvals": len(approvals),
        "outbound_eth_txs": len(outbound_transfers),
        "outbound_token_txs": outbound_tokens_count
    }

    return report
