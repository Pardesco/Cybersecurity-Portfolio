# Detection Rule: Pass-the-Hash

## Overview
Detects potential Pass-the-Hash (PtH) attacks by identifying network logons (Logon Type 3) utilizing NTLM authentication instead of Kerberos, especially when originating from unusual workstations.

## SPL Query
```spl
index=windows source="WinEventLog:Security" EventCode=4624 LogonType=3 AuthenticationPackageName="NTLM"
| where NOT match(WorkstationName, "^DC") 
| stats count by _time, TargetUserName, IpAddress, WorkstationName
| rename TargetUserName as Authenticated_User, IpAddress as Source_IP, WorkstationName as Source_Workstation
```

## Relevant Event IDs
- Windows Security Event ID **4624**: An account was successfully logged on.

## Explanation
In a modern Active Directory environment, most network authentication should utilize Kerberos. A Pass-the-Hash attack bypasses Kerberos by authenticating directly with the compromised NTLM hash of a user. This query looks for successful network logons (`EventCode=4624`, `LogonType=3`) that specifically fall back to `NTLM` authentication. 

## Tuning & False Positives
- **False Positives:** High. NTLM is still widely used by legacy systems, file shares, and poorly configured third-party applications.
- **Tuning:** This rule requires baseline tuning. You must profile your environment to understand which applications legitimately use NTLM. You can filter out known good workstations or service accounts. E.g., `| search NOT TargetUserName IN ("svc_legacyapp")`. Focus on privileged accounts (Domain Admins) authenticating via NTLM.