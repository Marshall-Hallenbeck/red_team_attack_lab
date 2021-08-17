# Red Team Attack Range

Original: https://github.com/splunk/attack_range_local/

## Purpose 

Every lab environment that I have come across (Splunk Attack Range, DetectionLab, etc) has been heavily focused on blue team controls and/or only runs in cloud environments.

As someone who doesn't want to pay extra money to host environments in AWS or Azure, this was quite annoying, so I decided to hack together something that runs locally and focuses on setting up a pentestable/red teamable environment, either for discovering new techniques, testing older TTPs, or staying up to date with the newest emerging threats.

## Building

The Red Team Attack Range can be built in... one way:

- **locally** with vagrant and virtualbox

## Installation



## Architecture
The virtualized deployment of Attack Range consists of:

- 1 Windows Domain Controller
  - 2019
- 1 Windows Server
  - 2019
- 2 Windows Workstation
  - Win10


#### Logging
Logging is disabled by default, since we firstly care about getting an environment up quickly and testing TTPs

The following log sources can be collected from the machines:

- Windows Event Logs (```index = win```)
- Sysmon Logs (```index = win```)
- Powershell Logs (```index = win```)
- Network Logs with Splunk Stream (```index = main```)
- Attack Simulation Logs from Atomic Red Team and Caldera (```index = attack```)

## Running
Attack Range supports different actions:

- Build Attack Range
- Perform Attack Simulation
- Destroy Attack Range
- Stop Attack Range
- Resume Attack Range
- Dump Attack Data

### Build Attack Range Local
- Build Attack Range Local
```
python attack_range_local.py -a build
```

### Perform Attack Simulation
- Perform Attack Simulation
```
python attack_range_local.py -a simulate -st T1003.001 -t attack-range-windows-domain-controller
```

### Show Attack Range Status
- Show Attack Range Status
```
python attack_range_local.py -lm
```

### Destroy Attack Range Local
- Destroy Attack Range Local
```
python attack_range_local.py -a destroy
```

### Stop Attack Range Local
- Stop Attack Range Local
```
python attack_range_local.py -a stop
```

### Resume Attack Range Local
- Resume Attack Range Local
```
python attack_range_local.py -a resume
```

## Dump Attack Data
- Dump Attack Range Data
```
python attack_range_local.py -a dump -dn dump_data_folder
```

## Features (from Splunk's Attack Range)
- [Splunk Server](https://github.com/splunk/attack_range/wiki/Splunk-Server)
  * Indexing of Microsoft Event Logs, PowerShell Logs, Sysmon Logs, DNS Logs, ...
  * Preconfigured with multiple TAs for field extractions
  * Out of the box Splunk detections with Enterprise Security Content Update ([ESCU](https://splunkbase.splunk.com/app/3449/)) App
  * Preinstalled Machine Learning Toolkit ([MLTK](https://splunkbase.splunk.com/app/2890/))
  * Splunk UI available through port 8000 with user admin
  * ssh connection over configured ssh key

- Bring Your Own Splunk Server
  * Send events to your own Splunk Server instance
  * Allows integration of automated attacks into your own detection engineering lifecycle


- [Splunk Enterprise Security](https://splunkbase.splunk.com/app/263/)
  * [Splunk Enterprise Security](https://splunkbase.splunk.com/app/263/) is a premium security solution requiring a paid license.
  * Enable or disable [Splunk Enterprise Security](https://splunkbase.splunk.com/app/263/) in [attack_range_local.conf](attack_range_local.conf)
  * Purchase a license, download it and store it in the apps folder to use it.

- [Splunk Phantom](https://www.splunk.com/en_us/software/splunk-security-orchestration-and-automation.html)
  * [Splunk Phantom](https://www.splunk.com/en_us/software/splunk-security-orchestration-and-automation.html) is a Security Orchestration and Automation platform
  * For a free development license (100 actions per day) register [here](https://my.phantom.us/login/?next=/)
  * Enable or disable [Splunk Phantom](https://www.splunk.com/en_us/software/splunk-security-orchestration-and-automation.html) in [attack_range_local.conf](attack_range_local.conf)

- [Windows Domain Controller & Window Server & Windows 10 Client](https://github.com/splunk/attack_range/wiki/Windows-Infrastructure)
  * Can be enabled, disabled and configured over [attack_range_local.conf](attack_range_local.conf)
  * Collecting of Microsoft Event Logs, PowerShell Logs, Sysmon Logs, DNS Logs, ...
  * Sysmon log collection with customizable Sysmon configuration
  * RDP connection over port 3389 with user Administrator

- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)
  * Attack Simulation with [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)
  * Will be automatically installed on target during first execution of simulate
  * Atomic Red Team already uses the new Mitre sub-techniques

- [Caldera](https://github.com/mitre/caldera)
  * Adversary Emulation with [Caldera](https://github.com/mitre/caldera)
  * Installed on the Splunk Server and available over port 8888 with user admin
  * Preinstalled Caldera agents on windows machines

- [Kali Linux](https://www.kali.org/)
  * Preconfigured Kali Linux machine for penetration testing
  * ssh connection over configured ssh key