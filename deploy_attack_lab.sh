#!/bin/bash

sudo apt update
sudo apt install -y linux-headers-generic vagrant ansible
sudo apt install -y virtualbox virtualbox-dkms
sudo gem install winrm-elevated
sudo gem install winrm
pip install "pywinrm>=0.2.2"
git clone https://github.com/Marshall-Hallenbeck/red_team_attack_lab
cd red_team_attack_lab
ansible-galaxy collection install community.windows chocolatey.chocolatey
vagrant plugin install vagrant-hostmanager vagrant-vbguest # vagrant-scp #vagrant-cachier
vagrant up