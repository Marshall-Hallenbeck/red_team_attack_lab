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
        self.vagrantfile += self.read_vagrant_file('windows-servers-vagrant')
        self.vagrantfile += '\r\n'
        self.vagrantfile += self.read_vagrant_file('windows10-vagrant')
        self.vagrantfile += '\r\n'
        self.vagrantfile += self.read_vagrant_file('win7/Vagrantfile')
        self.vagrantfile += '\r\n'
        self.vagrantfile += self.read_vagrant_file('kali-vagrant')
        self.vagrantfile += '\nend'
        with open('vagrant/Vagrantfile', 'w') as file:
            file.write(self.vagrantfile)
        self.log.info("Wrote Vagrantfile")

    def read_vagrant_file(self, path):
        j2_env = Environment(loader=FileSystemLoader('vagrant'), trim_blocks=True)
        template = j2_env.get_template(path)
        vagrant_file = template.render(self.config)
        return vagrant_file

    def build(self):
        self.log.info("Running build...")
        v1 = vagrant.Vagrant('vagrant/', quiet_stdout=False, quiet_stderr=False)
        try:
            v1.up(provision=True, provider="virtualbox")
        except Exception as e:
            self.log.error(f"Vagrant failed to build: {e}")
            sys.exit(1)

        self.log.info("The Red Team Attack Lab has been built using Vagrant successfully")
        self.list_machines()

    def destroy(self):
        self.log.info("Running destroy...")
        v1 = vagrant.Vagrant('vagrant/', quiet_stdout=False)
        v1.destroy()
        self.log.info("The Red Team Attack Lab has been destroyed using Vagrant successfully")

    def stop(self):
        self.log.info("Running stop...")
        v1 = vagrant.Vagrant('vagrant/', quiet_stdout=False)
        v1.halt()

    def resume(self):
        self.log.info("Running resume...")
        v1 = vagrant.Vagrant('vagrant/', quiet_stdout=False)
        v1.up()

    def list_machines(self):
        self.log.info('Getting Vagrant status...')
        v1 = vagrant.Vagrant('vagrant/', quiet_stdout=False)
        response = v1.status()
        status = []
        for stat in response:
            status.append([stat.name, stat.state, self.get_ip_address_from_machine(stat.name)])

        self.log.info("Vagrant status:\n" + tabulate(status, headers=['Name', 'Status', 'IP Address']))

    def get_ip_address_from_machine(self, box):
        pattern = 'config.vm.define "' + box + '"[\s\S]*?:private_network, ip: "([^"]+)'
        match = re.search(pattern, self.vagrantfile)
        return match.group(1)