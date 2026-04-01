<#
.SYNOPSIS
    Automates the configuration of a Windows Server 2022 Active Directory home lab.
.DESCRIPTION
    This script is designed to be run on a fresh Windows Server 2022 VM as an Administrator. 
    It will:
    - Set a static IP for the Domain Controller
    - Rename the computer to DC01
    - Install Active Directory Domain Services and create the 'lab.local' forest
    - After reboot: Create OUs, Users, configure GPOs, and install Sysmon + Splunk Forwarder.
#>

$DomainName = "lab.local"
$StaticIP = "192.168.56.10"
$Gateway = "192.168.56.1"
$SplunkIP = "192.168.56.1" # Host-Only adapter IP mapping to the host machine for localhost:8000
$SplunkForwarderUrl = "https://download.splunk.com/products/universalforwarder/releases/9.2.1/windows/splunkforwarder-9.2.1-78803f08aabb-x64-release.msi" # Example URL

# Check if running as Admin
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "Please run this script as Administrator."
    Exit
}

# 1. Determine Phase based on AD Domain Services Installation
$ADInstalled = Get-WindowsFeature AD-Domain-Services | Select-Object -ExpandProperty Installed

if (-not $ADInstalled) {
    Write-Host "[*] Phase 1: Initial Server Setup & AD Installation" -ForegroundColor Cyan
    
    # Configure Static IP (Assuming Host-Only Network Adapter)
    Write-Host "[*] Configuring Static IP ($StaticIP)..."
    $NetAdapter = Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -First 1
    New-NetIPAddress -InterfaceAlias $NetAdapter.Name -IPAddress $StaticIP -PrefixLength 24 -DefaultGateway $Gateway -ErrorAction SilentlyContinue | Out-Null
    Set-DnsClientServerAddress -InterfaceAlias $NetAdapter.Name -ServerAddresses "127.0.0.1"

    # Rename Computer
    Write-Host "[*] Renaming Computer to DC01..."
    Rename-Computer -NewName "DC01" -ErrorAction SilentlyContinue

    # Install AD DS Features
    Write-Host "[*] Installing AD Domain Services Features..."
    Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools

    # Install Forest (This will force a reboot)
    Write-Host "[*] Creating AD Forest '$DomainName'..." -ForegroundColor Yellow
    Write-Host "[!] The server will restart automatically after this step." -ForegroundColor Yellow
    $SafeModePassword = ConvertTo-SecureString "P@ssw0rdLab2026!" -AsPlainText -Force
    Install-ADDSForest -DomainName $DomainName -InstallDns:$true -CreateDnsDelegation:$false -DomainMode "WinThreshold" -ForestMode "WinThreshold" -SafeModeAdministratorPassword $SafeModePassword -Force:$true
    
} else {
    Write-Host "[*] Phase 2: Post-AD Configuration (OUs, Users, GPO, Sysmon, Splunk)" -ForegroundColor Cyan
    Import-Module ActiveDirectory

    try {
        $BaseDN = (Get-ADDomain).DistinguishedName
    } catch {
        Write-Warning "Domain not ready yet or script needs to be run after DC01 reboot."
        Exit
    }

    # 1. Create OUs
    $OUs = @("IT", "HR", "Finance")
    foreach ($OU in $OUs) {
        $OUPath = "OU=$OU,$BaseDN"
        if (-not (Get-ADOrganizationalUnit -Filter "Name -eq '$OU'")) {
            Write-Host "[+] Creating OU: $OU"
            New-ADOrganizationalUnit -Name $OU -Path $BaseDN
        }
    }

    # 2. Create Users
    $StandardUsers = @(
        @{Name="Alice Smith"; Sam="asmith"; OU="HR"},
        @{Name="Bob Jones"; Sam="bjones"; OU="Finance"},
        @{Name="Charlie Brown"; Sam="cbrown"; OU="IT"},
        @{Name="Diana Prince"; Sam="dprince"; OU="HR"},
        @{Name="Evan Wright"; Sam="ewright"; OU="Finance"}
    )
    $AdminUsers = @(
        @{Name="Admin One"; Sam="admin1"; OU="IT"},
        @{Name="Admin Two"; Sam="admin2"; OU="IT"}
    )

    $DefaultPassword = ConvertTo-SecureString "WelcomeToTheLab2026!" -AsPlainText -Force

    Write-Host "[+] Creating 5 Standard Users..."
    foreach ($User in $StandardUsers) {
        if (-not (Get-ADUser -Filter "SamAccountName -eq '$($User.Sam)'")) {
            New-ADUser -Name $User.Name -SamAccountName $User.Sam -UserPrincipalName "$($User.Sam)@$DomainName" -Path "OU=$($User.OU),$BaseDN" -AccountPassword $DefaultPassword -Enabled $true -PasswordNeverExpires $true
        }
    }

    Write-Host "[+] Creating 2 Admin Users..."
    foreach ($Admin in $AdminUsers) {
        if (-not (Get-ADUser -Filter "SamAccountName -eq '$($Admin.Sam)'")) {
            New-ADUser -Name $Admin.Name -SamAccountName $Admin.Sam -UserPrincipalName "$($Admin.Sam)@$DomainName" -Path "OU=$($Admin.OU),$BaseDN" -AccountPassword $DefaultPassword -Enabled $true -PasswordNeverExpires $true
            Add-ADGroupMember -Identity "Domain Admins" -Members $Admin.Sam
        }
    }

    # 3. Configure GPO (Password complexity and lockout)
    Write-Host "[+] Configuring Default Domain Policy (Password Complexity & Lockout)..."
    Set-ADDefaultDomainPasswordPolicy -Identity $DomainName -ComplexityEnabled $true -MinPasswordLength 10 -LockoutDuration (New-TimeSpan -Minutes 30) -LockoutObservationWindow (New-TimeSpan -Minutes 30) -LockoutThreshold 5

    # 4. Install Sysmon
    Write-Host "[+] Downloading and Installing Sysmon with SwiftOnSecurity config..."
    $SysmonDir = "C:\Tools\Sysmon"
    if (-not (Test-Path $SysmonDir)) { New-Item -ItemType Directory -Path $SysmonDir -Force | Out-Null }
    
    $SysmonZip = "$SysmonDir\Sysmon.zip"
    $SysmonConfig = "$SysmonDir\sysmonconfig-export.xml"

    if (-not (Get-Process "Sysmon64" -ErrorAction SilentlyContinue)) {
        Invoke-WebRequest -Uri "https://download.sysinternals.com/files/Sysmon.zip" -OutFile $SysmonZip
        Expand-Archive -Path $SysmonZip -DestinationPath $SysmonDir -Force
        Invoke-WebRequest -Uri "https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml" -OutFile $SysmonConfig
        
        Set-Location $SysmonDir
        .\Sysmon64.exe -accepteula -i $SysmonConfig | Out-Null
        Write-Host "    -> Sysmon installed successfully." -ForegroundColor Green
    } else {
        Write-Host "    -> Sysmon already running." -ForegroundColor Yellow
    }

    # 5. Splunk Universal Forwarder
    Write-Host "[+] Installing Splunk Universal Forwarder..."
    $SplunkInstaller = "C:\Tools\splunkforwarder.msi"
    if (-not (Test-Path $SplunkInstaller)) {
        Write-Host "    -> Downloading Splunk Forwarder MSI..."
        Invoke-WebRequest -Uri $SplunkForwarderUrl -OutFile $SplunkInstaller
    }
    
    if (-not (Get-Service "SplunkForwarder" -ErrorAction SilentlyContinue)) {
        Write-Host "    -> Running MSI Installer in quiet mode..."
        Start-Process -FilePath "msiexec.exe" -ArgumentList "/i $SplunkInstaller RECEIVING_INDEXER=`"$SplunkIP:9997`" WINEVENTLOG_SEC_ENABLE=1 WINEVENTLOG_SYS_ENABLE=1 WINEVENTLOG_APP_ENABLE=1 AGREETOLICENSE=Yes /quiet" -Wait -NoNewWindow
        Write-Host "    -> Splunk Forwarder installed successfully. Pointing to $SplunkIP" -ForegroundColor Green
    } else {
        Write-Host "    -> Splunk Forwarder already running." -ForegroundColor Yellow
    }

    Write-Host "[!!!] Phase 2 Configuration Complete! The lab architecture is ready." -ForegroundColor Green
}