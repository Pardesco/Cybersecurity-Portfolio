# Splunk Detection Rules Library

This directory contains Splunk Search Processing Language (SPL) queries designed to detect common attack patterns and Active Directory post-exploitation techniques from Windows Event Logs and Sysmon data.

## What It Detects
1. **Password Spraying:** Multiple failed logins across multiple accounts within a 5-minute window.
2. **Kerberoasting:** Event ID 4769, checking for RC4 encryption type (`0x17`).
3. **Pass-the-Hash:** Event ID 4624, Logon Type 3, focusing on NTLMv2 indicators.
4. **Local Admin Creation:** Event ID 4720 (user created) combined with Event ID 4732 (member added to local group).
5. **Malicious PowerShell:** PowerShell execution using encoded commands (Sysmon Event ID 1).

## Usage
Each rule contains the raw SPL, an explanation of what it detects, expected false positives, and recommendations for tuning the query within a SOC environment.

## Portfolio Value
Demonstrates advanced knowledge of log analysis, SIEM utilization (Splunk), Detection Engineering, and familiarity with attacker methodologies mapping to the MITRE ATT&CK framework.