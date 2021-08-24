# ORIGINAL: https://github.com/splunk/attack_range_local/
from jinja2 import Environment, FileSystemLoader
import vagrant
from tabulate import tabulate
import re
import sys
import textwrap


class VagrantController:

    def __init__(self, config, log):
        self.vagrantfile = ''
        self.config = config
        self.log = log
        self.create_vagrant_config()

    def create_vagrant_config(self):
        self.log.info('Creating Vagrantfile config from existing templates')

        self.vagrantfile = textwrap.dedent("""\
            Vagrant.configure("2") do |config|
            if Vagrant.has_plugin?("vagrant-hostmanager")
                 config.hostmanager.enabled = true
                 config.hostmanager.manage_host = true
                 config.hostmanager.ignore_private_ip = false
                 config.hostmanager.include_offline = true
            end\n""")

        self.vagrantfile += self.read_vagrant_file('windows-dc-vagrant')
        self.vagrantfile += '\r\n'
        self.vagrantfile += self.read_vagrant_file('windows10-vagrant')
        self.vagrantfile += '\r\n'
        self.vagrantfile += self.read_vagrant_file('windows-servers-vagrant')
        self.vagrantfile += '\r\n'
        self.vagrantfile += self.read_vagrant_file('kali-vagrant')
        self.vagrantfile += '\nend'
        with open('vagrant/Vagrantfile', 'w') as file:
            file.write(self.vagrantfile)
        self.log.info("Wrote Vagrantfile\n")

    def read_vagrant_file(self, path):
        j2_env = Environment(loader=FileSystemLoader('vagrant'), trim_blocks=True)
        template = j2_env.get_template(path)
        vagrant_file = template.render(self.config)
        return vagrant_file

    def build(self):
        self.log.info("[action] > build\n")
        v1 = vagrant.Vagrant('vagrant/', quiet_stdout=False, quiet_stderr=False)
        try:
            v1.up(provision=True, provider="virtualbox")
        except Exception as e:
            self.log.error(f"vagrant failed to build: {e}")
            sys.exit(1)

        self.log.info("attack_lab has been built using vagrant successfully")
        self.list_machines()

    def destroy(self):
        self.log.info("[action] > destroy\n")
        v1 = vagrant.Vagrant('vagrant/', quiet_stdout=False)
        v1.destroy()
        self.log.info("attack_lab has been destroy using vagrant successfully")

    def stop(self):
        print("[action] > stop\n")
        v1 = vagrant.Vagrant('vagrant/', quiet_stdout=False)
        v1.halt()

    def resume(self):
        print("[action] > resume\n")
        v1 = vagrant.Vagrant('vagrant/', quiet_stdout=False)
        v1.up()

    def get_ip_address_from_machine(self, box):
        pattern = 'config.vm.define "' + box + '"[\s\S]*?:private_network, ip: "([^"]+)'
        match = re.search(pattern, self.vagrantfile)
        return match.group(1)

    def check_targets_running_vagrant(self, target, log):
        v1 = vagrant.Vagrant('vagrant/', quiet_stdout=False)
        status = v1.status()

        found_box = False
        for stat in status:
            if stat.name == target:
                found_box = True
                if not (stat.state == 'running'):
                    log.error(target + ' not running.')
                    sys.exit(1)
                break
        if not found_box:
            log.error(target + ' not found as vagrant box.')
            sys.exit(1)

    def list_machines(self):
        print()
        print('Vagrant Status\n')
        v1 = vagrant.Vagrant('vagrant/', quiet_stdout=False)
        response = v1.status()
        status = []
        for stat in response:
            status.append([stat.name, stat.state, self.get_ip_address_from_machine(stat.name)])

        print(tabulate(status, headers=['Name', 'Status', 'IP Address']))
        print()