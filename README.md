# Red Team Attack Lab

Disclaimer: right now this is in a heavy development state.  This is also my first time really using Vagrant & Ansible.
The playbooks and tasks are all messed up.

## Description

Every lab environment that I have come across (Splunk Attack Range, DetectionLab, etc) has been heavily focused on blue team controls and/or only runs in cloud environments.

As someone who doesn't want to pay extra money to host environments in AWS or Azure, this was quite annoying, so I decided to hack together something that runs locally and focuses on setting up a pentestable/red teamable environment, either for discovering new techniques, testing older TTPs, or staying up to date with the newest emerging threats.

## Installation
### Dependencies
```
sudo apt-get update 
sudo apt-get install -y python3-dev linux-headers-generic python-dev unzip python-pip vagrant virtualbox virtualbox-dkms python-virtualenv git
sudo gem install winrm-elevated
sudo gem install winrm
```
```
ansible-galaxy collection install community.windows chocolatey.chocolatey
vagrant plugin install vagrant-hostmanager vagrant-vbguest
```
```
# Create a Virtualenv for best practice
virtualenv -p python3 venv_rtal
source venv_rtal/bin/activate
pip install -r requirements.txt
```

## How to Run

### Full Build (may take 1-1.5 hours!)
```
# ensure it is python3!
python red_team_attack_lab.py -a build
```
### Specific Build
```
# ensure it is python3!
python red_team_attack_lab.py -a create_config
cd vagrant
vagrant up dc01 win2019-adcs win10-dev kali
```
Other hosts (see Architecture):
- win10-1
- win10-2
- win2019-1

## Architecture
TODO: create architecture document...

Currently supported hosts:

- 1 Windows Domain Controller
  - Windows Server 2019
    - dc01
- 2 Windows Servers
  - Windows Server 2019
    - win2019-1
  - Windows Server 2019 with Active Directory Certificate Services + Web Enrollment + Web Service for Petit Potam
    - win2019-adcs
- 3 Windows Workstations
  - Win10
    - win10-1
    - win10-2
  - Win10 Development Environment (Customized via Chocolatey)
    - win10-dev
- 1 Kali Box (Customized)
  - kali

## TODO LIST
- [x] Automate ADCS deployment
  - [x] Automate ADCS Certificate Authority
  - [x] Automate ADCS Enrollment Web Service
  - [x] Automate ADCS Web Enrollment
- [x] Dynamic domain name
    - [x] default to "attacklab.local"
    - [x] Ensure proper usage of config variables so we only have to change it in one location
- [ ] Change domain admin username to "Admin"
    - [ ] Ensure proper usage of config variables so we only have to change it in one location
- [ ] Ensure local administrator account is properly created seperate from DA Admin account
- [ ] Automatically remove hosts from AD on `vagrant destroy`
    - REF: https://www.vagrantup.com/docs/triggers/usage
    - REF: https://docs.ansible.com/ansible/latest/collections/community/windows/win_domain_computer_module.html#parameter-state
    - REF: https://stackoverflow.com/questions/40087032/how-to-run-a-vagrant-task-on-vagrant-destroy
- [ ] Clean up Configs
  - [ ] Vagrant Configs
  - [ ] Base ansible configuration values in one place
- [ ] Improve Windows QoL with scripts
    - [ ] Steal from DetectionLab
- [ ] Add hosts
    - [ ] Metasploitable 3 - https://github.com/rapid7/metasploitable3
      - [ ] Windows
      - [ ] Ubuntu
    - [ ] Server 2016
    - [ ] Server 2012
    - [ ] Server 2022
    - [ ] Windows 7
    - [ ] Ubuntu Server 20
    - [ ] Ubuntu Server 18
    - [ ] Ubuntu Desktop 20
    - [ ] Ubuntu Desktop 18
    - [ ] CentOS ?
- [ ] Add documentation
    - [ ] Installation
    - [ ] Default credentials & config variables
    - [ ] How to get running
    - [ ] Debugging commands
    - [ ] How to add/update/test/add stuff
      - [ ] Common pitfalls
    - [ ] Lab architecture diagram
    - [ ] Existing AD vulnerabilities
      - /vulns
    - [ ] FAQ
- [ ] Clean up red_team_attack_lab.py
    - [ ] FIX: can't run the range from any path due to config reading, but updating the config reading breaks the VagrantController reading the vagrant files due to bad path handling as well
      - [ ] Also make the config parser not bad - get rid of the custom config parser completely
- [ ] Add attack walkthroughs
    - [ ] /vulns/walkthroughs folder
- [ ] Make Ansible faster
  - REF: https://docs.ansible.com/ansible/latest/user_guide/playbooks_async.html
  - https://docs.ansible.com/ansible/latest/user_guide/playbooks_strategies.html