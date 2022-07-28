# Setting up RTAL on Windows
Disclaimer: there can be a ton of things that don't make this work, and almost none of them describe errors well. This is a side effect of using WSL. 

I can only provide so much help on this setup process since it's very finnicky, and it works best if you start on a completely clean install.

If you run into an error, check out the [errors](#errors) section below, and if it's not in there, do some Googling.

Tested on Windows 10 Home & Pro & 11 Pro

## Steps
1) Install WSL & whatever distro (tested on Ubuntu 20.04 via `wsl --install -d Ubuntu`)
2) Set WSL version to 1
   * wsl --set-version Ubuntu 1
   * Check with “wsl -l -v”
   * This is needed for port forwarding due to how WSL1 v WSL2
3) Windows Prereqs
   1) Fix Windows janky virtualization to work with WSL
      * bcdedit /set hypervisorlaunchtype off
      * DISM /Online /Disable-Feature:Microsoft-Hyper-V
      * reboot
   2) Install Virtualbox  6.1.26
      * https://download.virtualbox.org/virtualbox/6.1.26/VirtualBox-6.1.26-145957-Win.exe 
   3) Install Vagrant 2.2.6
      * https://releases.hashicorp.com/vagrant/2.2.6/vagrant_2.2.6_x86_64.msi 
   4) Make sure the following Windows Features are enabled:
      * Virtual Machine Platform
      * Windows Subsystem for Linux
4) Linux Dependencies (run everything as root `sudo -u root -i`)
    * `sudo apt-get update`
    * `sudo apt-get install -y linux-headers-generic ansible ruby-dev libarchive-tools`
      * libarchive-tools is for Ubuntu 20.04, see https://stackoverflow.com/a/65629036 
    * Install Vagrant 2.2.6
      * `sudo apt install vagrant`
        * As of 7/22/22 Ubuntu uses 2.2.6
    * Install Ansible/Vagrant/Ruby plugins
      * `sudo ansible-galaxy collection install community.windows chocolatey.chocolatey `
      * `sudo vagrant plugin install vagrant-hostmanager vagrant-vbguest `
      * `sudo gem install winrm-elevated`
      * `sudo gem install winrm`
    * Update .bashrc (or whatever config file you use)
      * `export VAGRANT_WSL_ENABLE_WINDOWS_ACCESS="1"`
      * `export PATH="/mnt/c/Windows/System32:/mnt/c/Windows/System32/WindowsPowerShell/v1.0:/mnt/c/Hashicorp/Vagrant/bin/:$PATH"`

# Errors
## VBoxManage startvm
```
There was an error while executing `VBoxManage`, a CLI used by Vagrant
for controlling VirtualBox. The command and stderr is shown below.

Command: ["startvm", "f71acfb8-5456-4fa3-85f8-e1a7d744f416", "--type", "gui"]

Stderr: VBoxManage.exe: error: Failed to get device handle and/or partition ID for 0000000001688b80 (hPartitionDevice=0000000000000c29, Last=0xc0000002/1) (VERR_NEM_VM_CREATE_FAILED)
VBoxManage.exe: error: Details: code E_FAIL (0x80004005), component ConsoleWrap, interface IConsole
```
### Cause
Windows has really stupid virtualization
### Fix
```
bcdedit /set hypervisorlaunchtype off
DISM /Online /Disable-Feature:Microsoft-Hyper-V
reboot
```
### Notes
Even if you don’t have Microsoft-Hyper-V enabled in the Windows Features you need to do this... Really stupid and it makes no sense.
https://forums.virtualbox.org/viewtopic.php?f=6&t=101232 &
https://forums.virtualbox.org/viewtopic.php?f=25&t=97412 

## Fuse Device Not Found
```
fuse: device not found, try 'modprobe fuse' first

Cannot mount AppImage, please check your FUSE setup.
You might still be able to extract the contents of this AppImage
if you run it with the --appimage-extract option.
See https://github.com/AppImage/AppImageKit/wiki/FUSE
for more information
open dir error: No such file or directory
```
### Cause
Vagrant version 2.2.19 is wonky. It worked on two of my computers, but not my Windows 11 Pro Laptop.
### Fix
Use Vagrant Version 2.2.6 (This version is chose because it’s the one that’s installed via `apt install vagrant` in Ubuntu 20)
Download Links: https://releases.hashicorp.com/vagrant/2.2.6/
Windows MSI: https://releases.hashicorp.com/vagrant/2.2.6/vagrant_2.2.6_x86_64.msi 

## Windows & Ansible
```
Windows is not officially supported for the Ansible Control Machine.
Please check https://docs.ansible.com/intro_installation.html#control-machine-requirements
    dc01: Running ansible-playbook...
The Ansible software could not be found! Please verify
that Ansible is correctly installed on your host system.

If you haven't installed Ansible yet, please install Ansible
on your host system. Vagrant can't do this for you in a safe and
automated way.
Please check https://docs.ansible.com for more information.
```
### Cause
Ansible isn’t supported on Windows...
### Fix
It’s attempting to use `vagrant.exe` not `vagrant`, so make sure you are calling the Linux binary, not Windows

## Vagrant Powershell Minimum Required Version
```
Vagrant failed to initialize at a very early stage:

The version of powershell currently installed on this host is less than
the required minimum version. Please upgrade the installed version of
powershell to the minimum required version and run the command again.

  Installed version: /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe: Invalid argument

  Minimum required version: 3
```
### Cause
Essentially some sort of janky Windows/WSL permissions
### Fix
Run Powershell as administrator and put the inserted PATH variables in FRONT of the existing PATH e.g. `export PATH=”/blah/blah/:$PATH”

You can test this by running `powershell.exe` inside WSL and see if you can `dir` or anything
## Vagrant Not Properly Using Virtualbox Provider
Either `vagrant status` is showing “hyperv” or some other provider, and attempting to force Virtualbox like `vagrant up --provider virtualbox` shows bullshit vboxmanage errors such as...
```
The provider 'virtualbox' that was requested to back the machine
'dc01' is reporting that it isn't usable on this system. The
reason is shown below:

VirtualBox is complaining that the kernel module is not loaded. Please
run `VBoxManage --version` or open the VirtualBox GUI to see the error
message which should contain instructions on how to fix this error.
```
### Cause
Virtualbox is installed on WSL
### Fix
Uninstall Virtualbox from WSL

This isn’t as easy as `sudo apt purge virtualbox*` or anything, because using the run script will install in /opt/Virtualbox... so you gotta uninstall it via `/opt/Virtualbox/uninstall.sh`

Check the config location at `cat /etc/vbox/vbox.cfg` for install loc if it’s not in /opt/
### References
https://askubuntu.com/a/927296 

## Vagrant Plugins Failed to Initialize
```
Vagrant failed to initialize at a very early stage:

The plugins failed to initialize correctly. This may be due to manual
modifications made within the Vagrant home directory. Vagrant can
attempt to automatically correct this issue by running:

  vagrant plugin repair

If Vagrant was recently updated, this error may be due to incompatible
versions of dependencies. To fix this problem please remove and re-install
all plugins. Vagrant can attempt to do this automatically by running:

  vagrant plugin expunge --reinstall

Or you may want to try updating the installed plugins to their latest
versions:

  vagrant plugin update

Error message given during initialization: Unable to resolve dependency: user requested 'vagrant-hostmanager (= 1.8.9)'
```
### Cause
Reinstalled Vagrant without reinstalling the previous plugins
### Fix
Run `vagrant plugin repair`
