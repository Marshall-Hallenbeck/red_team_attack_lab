# Red Team Attack Lab

Disclaimer: right now this is in a heavy development state. This is also my first time really using Vagrant & Ansible.
The playbooks and tasks are all messed up. I still have a bunch of stuff from the Splunk Attack Range added, but I will probably nuke all of that so there's no issues. Right now I'm just using them as a reference.

Original: https://github.com/splunk/attack_range_local/

## Description

Every lab environment that I have come across (Splunk Attack Range, DetectionLab, etc) has been heavily focused on blue team controls and/or only runs in cloud environments.

As someone who doesn't want to pay extra money to host environments in AWS or Azure, this was quite annoying, so I decided to hack together something that runs locally and focuses on setting up a pentestable/red teamable environment, either for discovering new techniques, testing older TTPs, or staying up to date with the newest emerging threats.

## Installation
To be filled in...

## How to Run
To be filled in....

## Architecture
TODO: create architecture document...

###Currently supported hosts:
- 1 Windows Domain Controller
  - Windows Server 2019
    - dc01
- 2 Windows Servers
  - Windows Server 2019
    - win2019-1
  - Windows Server 2019 with Active Directory Certificate Services
    - win2019-adcs
      - Currently working on adding Web Enrollment and Web Service
- 3 Windows Workstations
  - Win10
    - win10-1
    - win10-2
  - Win10 Development Environment (Customized via Chocolatey)
    - win10-dev
- 1 Kali Box (Customized)
  - kali