from parser import parse_eml
from vt_client import check_url
from whois_client import get_domain_age_days
import json

def analyze_email(eml_path):
    """Core logic to score and classify the email."""
    print(f"[*] Parsing email: {eml_path}")
    data = parse_eml(eml_path)
    
    report = {
        "classification": "CLEAN",
        "evidence": [],
        "parsed_data": data,
        "url_analysis": []
    }
    
    malicious_score = 0
    suspicious_score = 0
    
    # 1. Check From vs Reply-To mismatch
    from_addr = str(data.get("from", "")).lower()
    reply_to = str(data.get("reply_to", "")).lower()
    
    if reply_to and from_addr and reply_to not in from_addr:
        report["evidence"].append(f"Mismatch between From ({from_addr}) and Reply-To ({reply_to})")
        suspicious_score += 1

    # 2. Check Authentication Results (SPF/DKIM/DMARC)
    auth_results = str(data.get("authentication_results", "")).lower()
    if auth_results:
        if "spf=fail" in auth_results or "spf=softfail" in auth_results:
            report["evidence"].append("SPF validation failed")
            suspicious_score += 1
        if "dkim=fail" in auth_results:
            report["evidence"].append("DKIM validation failed")
            suspicious_score += 1
        if "dmarc=fail" in auth_results:
            report["evidence"].append("DMARC validation failed")
            suspicious_score += 1
            
    # 3. Analyze URLs
    urls = data.get('urls', [])
    print(f"[*] Found {len(urls)} unique URLs. Analyzing...")
    for url in urls:
        url_report = {"url": url, "vt_stats": None, "domain_age_days": None, "flags": []}
        
        # WHOIS Domain Age
        age = get_domain_age_days(url)
        url_report["domain_age_days"] = age
        if age is not None and age < 30:
            flag = f"Newly registered domain ({age} days old)"
            url_report["flags"].append(flag)
            report["evidence"].append(f"URL uses newly registered domain: {url} - {flag}")
            suspicious_score += 2
            
        # VirusTotal Check
        vt_stats = check_url(url)
        url_report["vt_stats"] = vt_stats
        if vt_stats:
            malicious_count = vt_stats.get("malicious", 0)
            suspicious_count = vt_stats.get("suspicious", 0)
            if malicious_count > 0:
                flag = f"Flagged by {malicious_count} security vendors on VirusTotal"
                url_report["flags"].append(flag)
                report["evidence"].append(f"Malicious URL detected: {url} - {flag}")
                malicious_score += 5
            elif suspicious_count > 0:
                suspicious_score += 1
                
        report["url_analysis"].append(url_report)
        
    # Determine Final Classification
    if malicious_score > 0:
        report["classification"] = "MALICIOUS"
    elif suspicious_score >= 2:
        report["classification"] = "SUSPICIOUS"
        
    return report

def print_report(report):
    """Outputs the formatted CLI report."""
    print("\n" + "="*70)
    print(f"PHISHING TRIAGE REPORT: {report['classification']}")
    print("="*70)
    
    print("\n[EMAIL METADATA]")
    print(f"From:     {report['parsed_data']['from']}")
    print(f"Reply-To: {report['parsed_data']['reply_to']}")
    print(f"Subject:  {report['parsed_data']['subject']}")
    print(f"Date:     {report['parsed_data']['date']}")
    
    print(f"\n[ROUTING & AUTHENTICATION]")
    print(f"Received IPs: {', '.join(report['parsed_data']['received_ips']) if report['parsed_data']['received_ips'] else 'None extracted'}")
    auth = report['parsed_data']['authentication_results']
    if auth:
        print(f"Auth Results: {auth[:120]}..." if len(auth) > 120 else f"Auth Results: {auth}")
    else:
        print("Auth Results: Not found")
        
    print("\n[EVIDENCE OF MALICE]")
    if report["evidence"]:
        for ev in report["evidence"]:
            print(f" [!] {ev}")
    else:
        print(" [+] No strong indicators of phishing found.")
        
    if report["url_analysis"]:
        print("\n[URL ANALYSIS]")
        for u in report["url_analysis"]:
            print(f" - {u['url']}")
            if u['domain_age_days'] is not None:
                print(f"   Domain Age: {u['domain_age_days']} days")
            if u['vt_stats']:
                print(f"   VT Score: {u['vt_stats'].get('malicious', 0)} malicious, {u['vt_stats'].get('suspicious', 0)} suspicious")
            print()
    print("="*70)
