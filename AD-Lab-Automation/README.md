# Active Directory Lab Automation (Infrastructure as Code)

This folder contains the automation script (`Setup-ADLab.ps1`) to rapidly stand up an Active Directory home lab on a fresh Windows Server 2022 instance. 

## What It Does
When run as an Administrator on a fresh server, the script performs a two-phase deployment:
1. **Phase 1:** Configures a static IP (`192.168.56.10`), renames the machine to `DC01`, installs the AD DS role, and creates the `lab.local` forest. *The server will reboot automatically.*
2. **Phase 2:** Run the script again after the reboot. It will create OUs (IT, HR, Finance), generate 7 test users (5 standard, 2 admin), configure a default domain policy with password complexity/lockout thresholds, install **Sysmon** (with the SwiftOnSecurity config), and install the **Splunk Universal Forwarder** to ship logs to the host machine.

## How to Run It
1. Install a fresh Windows Server 2022 VM in VirtualBox.
2. Ensure the VM's network is set to the **Host-Only Adapter** (`192.168.56.x` subnet).
3. Copy this script to the VM.
4. Open an Administrator PowerShell prompt and run:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force
   .\Setup-ADLab.ps1
   ```
5. Wait for the reboot. Log in as `LAB\Administrator`.
6. Run the script again to complete the configuration.

## Portfolio Value
Demonstrates **Infrastructure-as-Code (IaC)** principles, knowledge of Active Directory administration (OUs, Users, GPOs), endpoint visibility (Sysmon), and log aggregation (Splunk Forwarder). Being able to automate lab rebuilding is a critical skill for modern Security Operations and DevSecOps engineering.