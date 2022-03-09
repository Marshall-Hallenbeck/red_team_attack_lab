# Red Team Attack Lab

Disclaimer: right now this is in a development state.  This is also my first time really using Vagrant & Ansible.

## Description

A virtual environment with various realistic operating system and vulnerabilities for red teamers to play with

### Impetus
Every lab environment that I have come across (Splunk Attack Range, DetectionLab, etc)
has been heavily focused on blue team controls and/or only runs in cloud environments.

As someone who doesn't want to pay extra money to host environments in AWS or Azure,
this was quite annoying, so I decided to hack together something that runs locally.

My main focus is on setting up a red teamable environment either for testing the development of tools,
discovering new techniques, testing older TTPs,  or staying up to date with the newest emerging threats.

## Installation
### Dependencies
```
sudo apt-get update 
sudo apt-get install -y linux-headers-generic vagrant virtualbox virtualbox-dkms
sudo gem install winrm-elevated
sudo gem install winrm
```
```
ansible-galaxy collection install community.windows chocolatey.chocolatey
vagrant plugin install vagrant-hostmanager vagrant-vbguest
```

## How to Run

### Full Build (may take ~2 hours!)
```
vagrant up
```
If a host fails to connect via WinRM after spinning up (intermittent issue), just re-run the provisioning via `vagrant provision $host`.

### Specific Build
```
vagrant up dc01 win10-1 win10-dev kali
```
For full list of hosts see [hosts](docs/hosts.md)

## Architecture
TODO: create architecture document...

See [hosts](docs/hosts.md)
