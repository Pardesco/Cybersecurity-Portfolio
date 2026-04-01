# Detection Rule: Password Spraying

## Overview
Detects a high volume of failed authentication attempts across multiple unique user accounts from a single source IP address within a short time window.

## SPL Query
```spl
index=windows source="WinEventLog:Security" EventCode=4625
| bucket _time span=5m
| stats count dc(TargetUserName) as unique_accounts values(TargetUserName) as targeted_users by _time, IpAddress
| where unique_accounts >= 5
| sort - _time
| rename IpAddress as Source_IP, count as Total_Failed_Logins, unique_accounts as Unique_Accounts_Targeted
```

## Relevant Event IDs
- Windows Security Event ID **4625**: An account failed to log on.

## Explanation
Password spraying involves an attacker trying a single common password (or a small list) against many user accounts to avoid account lockouts. This query groups failed logins (`EventCode=4625`) into 5-minute buckets (`span=5m`) and counts the number of distinct (`dc()`) usernames targeted from a single source IP. If an IP targets 5 or more unique accounts in 5 minutes, it flags it as a potential spray.

## Tuning & False Positives
- **False Positives:** Misconfigured applications, scripts with expired credentials, or aggressive vulnerability scanners. 
- **Tuning:** Adjust the `span=5m` and `unique_accounts >= 5` thresholds based on the size of your environment. You can also exclude known scanner IPs using `| search NOT IpAddress IN ("192.168.1.50", "10.0.0.15")`.