# Detection Rule: Kerberoasting

## Overview
Detects potential Kerberoasting activity by looking for Service Ticket Grants (TGS) that use weak RC4 encryption (0x17), which are easier to crack offline.

## SPL Query
```spl
index=windows source="WinEventLog:Security" EventCode=4769 TicketOptions="0x40810000" TicketEncryptionType="0x17"
| where NOT match(TargetUserName, "\\$$")
| stats count by _time, TargetUserName, IpAddress, ServiceName
| rename TargetUserName as Requesting_User, IpAddress as Source_IP, ServiceName as Target_Service
```

## Relevant Event IDs
- Windows Security Event ID **4769**: A Kerberos service ticket was requested.

## Explanation
Kerberoasting involves an attacker requesting a TGS (Ticket Granting Service) ticket for a service account. The ticket is encrypted with the service account's NTLM hash. If the encryption type is RC4 (`0x17`), it can be efficiently cracked offline to retrieve the plaintext password. This query looks for Event ID 4769 where `TicketEncryptionType="0x17"` and excludes computer accounts (`TargetUserName!="*$"`), focusing on potentially vulnerable service accounts. 

## Tuning & False Positives
- **False Positives:** Legacy applications or systems that do not support modern AES encryption (AES128 `0x11` or AES256 `0x12`).
- **Tuning:** If legacy systems are expected, build an exclusion list for specific service accounts or IP addresses. Migrating your domain to require AES encryption is the ultimate mitigation.