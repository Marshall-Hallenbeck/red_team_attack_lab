#!/bin/bash

sudo apt-get update 
sudo apt-get install -y linux-headers-generic vagrant virtualbox virtualbox-dkms
sudo gem install winrm-elevated
sudo gem install winrm
git clone https://github.com/Marshall-Hallenbeck/red_team_attack_lab
cd red_team_attack_lab
ansible-galaxy collection install community.windows chocolatey.chocolatey
vagrant plugin install vagrant-hostmanager vagrant-vbguest # vagrant-scp #vagrant-cachier
vagrant up