## OtterTools ʕ •ᴥ•ʔ
This is a repo were I store the main tools i use when doing CTFs and Pentesting projects.

### Cloning the repo
To properly clone the repository and all its submodules use
```
git clone --recurse-submodules https://github.com/otterpwn/ottertools.git
```

### Setting up the repo for use
I installed the repository in my home directory (`/home/otter/ottertools`) so I added an alias to my `.bashrc` and `.zshrc`
```bash
alias ottertools='cd ~/ottertools;tree -L 2'
```

This alias will allow the user to type `ottertools` as a command, get dropped into the directory and get a list of all available tools.

```
.
├── active_directory
│   ├── AdExplorer
│   ├── ADFSDump.exe
│   ├── ADFSpoof
│   ├── adidnsdump
│   ├── ADRecon
│   ├── getnthash.py
│   ├── gettgtpkinit.py
│   ├── gpp-decrypt
│   ├── Group3r.exe
│   ├── Inveigh.exe
│   ├── Inveigh.ps1
│   ├── Invoke-TheHash
│   ├── kerbrute_linux_amd64
│   ├── LAPSToolkit.ps1
│   ├── mimikatz
│   ├── nc64.exe
│   ├── noPac
│   ├── PetitPotam
│   ├── Powermad.ps1
│   ├── PowerSCCM.ps1
│   ├── PowerView.ps1
│   ├── Rubeus.exe
│   ├── SharpHound.exe
│   ├── SharpHound.ps1
│   ├── SharpView.exe
│   ├── Snaffler.exe
│   └── windapsearch
├── cracking
│   └── hashcat
├── credentials_attacks
│   ├── cme
│   ├── cupp
│   ├── DefaultCreds-cheat-sheet
│   ├── DomainPasswordSpray.ps1
│   ├── firefox_decrypt
│   ├── KeyTabExtract
│   ├── LaZagne
│   ├── o365spray
│   └── username-anarchy
├── cryptography
│   └── RsaCtfTool
├── enumeration
│   ├── enum4linux
│   └── peas
├── network_protocols
│   ├── evil-winrm
│   ├── impacket
│   ├── Responder
│   ├── smbmap
│   └── ssh-audit
├── phishing
│   └── modlishka
├── README.md
├── reporting
│   └── writehat
├── reverse_engineering
│   └── AvaloniaILSpy
└── tunnelling
    ├── chisel
    └── ligolo
```
