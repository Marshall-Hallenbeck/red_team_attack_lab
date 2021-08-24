#!/bin/bash

# ORIGINAL: https://github.com/splunk/attack_range_local/
sudo apt-get update 
sudo apt-get install -y python3-dev linux-headers-generic python-dev unzip python-pip vagrant virtualbox virtualbox-dkms python-virtualenv git
sudo gem install winrm-elevated
sudo gem install winrm
git clone https://github.com/Marshall-Hallenbeck/red_team_attack_lab && cd red_team_attack_lab
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install community.windows chocolatey.chocolatey
python red_team_attack_lab.py -a build
