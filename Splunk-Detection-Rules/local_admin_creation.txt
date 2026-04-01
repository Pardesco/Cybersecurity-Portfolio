# Detection Rule: Local Admin Creation

## Overview
Detects when a new user account is created and subsequently added to a highly privileged local group, such as the local Administrators group.

## SPL Query
```spl
index=windows source="WinEventLog:Security" (EventCode=4720 OR EventCode=4732)
| transaction TargetUserName maxspan=5m
| search EventCode=4720 EventCode=4732 TargetSid="*S-1-5-32-544"
| table _time, host, SubjectUserName, TargetUserName, TargetSid
| rename host as Hostname, SubjectUserName as Admin_Who_Created, TargetUserName as New_Admin_Account
```

## Relevant Event IDs
- Windows Security Event ID **4720**: A user account was created.
- Windows Security Event ID **4732**: A member was added to a security-enabled local group.
- **TargetSid `S-1-5-32-544`**: The well-known SID for the built-in local Administrators group.

## Explanation
Attackers often establish persistence on a compromised machine by creating a new backdoor account and adding it to the local Administrators group. This query uses the `transaction` command to correlate two events: an account creation (`4720`) and an addition to a local group (`4732`) involving the newly created account (`TargetUserName`) within a 5-minute window (`maxspan=5m`), specifically checking if the group added to is the Administrators group (`S-1-5-32-544`).

## Tuning & False Positives
- **False Positives:** Authorized system administrators or automated IT provisioning scripts creating local admin accounts for specific operational needs.
- **Tuning:** Filter out known Helpdesk provisioning accounts from `SubjectUserName`. If your organization uses LAPS (Local Administrator Password Solution), local admin creation should be incredibly rare and treated as a high-fidelity alert.