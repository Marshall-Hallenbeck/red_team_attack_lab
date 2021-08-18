from jinja2 import Environment, FileSystemLoader
import vagrant
from tabulate import tabulate
import re
import ansible_runner
import sys
import os
import yaml
from modules import splunk_sdk


class VagrantController:

    def __init__(self, config, log):
        self.vagrantfile = ''
        self.config = config
        self.log = log
        self.create_vagrant_config()

    def create_vagrant_config(self):
        self.log.info('Creating Vagrantfile config from existing templates')

        self.vagrantfile = 'Vagrant.configure("2") do |config| \n \n'

        if self.config['install_es'] == '1':
            self.config['splunk_es_app_version'] = re.findall(r'\d+', self.config['splunk_es_app'])[0]

        if self.config['phantom_server'] == '1':
            self.vagrantfile += self.read_vagrant_file('phantom-server/Vagrantfile')
            self.vagrantfile += '\n\n'
        if self.config['splunk_server'] == '1':
            self.vagrantfile += self.read_vagrant_file('splunk_server/Vagrantfile')
            self.vagrantfile += '\n\n'
        if self.config['splunk_server'] == '0' and self.config['caldera_server'] == 1:
            self.vagrantfile += self.read_vagrant_file('caldera-server/Vagrantfile')
            self.vagrantfile += '\n\n'
        if self.config['windows_domain_controller'] == '1':
            self.vagrantfile += self.read_vagrant_file('windows-domain-controller/Vagrantfile')
            self.vagrantfile += '\n\n'
        if self.config['windows_client'] == '1':
            self.vagrantfile += self.read_vagrant_file('windows10/Vagrantfile')
            self.vagrantfile += '\n\n'
        if self.config['windows_server'] == '1':
            self.vagrantfile += self.read_vagrant_file('windows-server/Vagrantfile')
            self.vagrantfile += '\n\n'
        if self.config['kali_machine'] == '1':
            self.vagrantfile += self.read_vagrant_file('kali/Vagrantfile')
            self.vagrantfile += '\n\n'
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

        self.log.info("attack_range has been built using vagrant successfully")
        self.list_machines()

    def destroy(self):
        self.log.info("[action] > destroy\n")
        v1 = vagrant.Vagrant('vagrant/', quiet_stdout=False)
        v1.destroy()
        self.log.info("attack_range has been destroy using vagrant successfully")

    def stop(self):
        print("[action] > stop\n")
        v1 = vagrant.Vagrant('vagrant/', quiet_stdout=False)
        v1.halt()

    def resume(self):
        print("[action] > resume\n")
        v1 = vagrant.Vagrant('vagrant/', quiet_stdout=False)
        v1.up()

    def simulate(self, target, simulation_techniques, simulation_atomics):

        # check if specific atomics are used then it's not allowed to multiple techniques
        techniques_arr = simulation_techniques.split(',')
        if (len(techniques_arr) > 1) and (simulation_atomics != 'no'):
            self.log.error('ERROR: if simulation_atomics are used, only a single simulation_technique is allowed.')
            sys.exit(1)

        run_specific_atomic_tests = 'True'
        if simulation_atomics == 'no':
            run_specific_atomic_tests = 'False'

        # get ip address from machine
        self.check_targets_running_vagrant(target, self.log)
        target_ip = self.get_ip_address_from_machine(target)
        runner = ansible_runner.run(
            private_data_dir='.',
            cmdline=str('-i ' + target_ip + ', '),
            roles_path="ansible/roles",
            playbook='ansible/atomic_red_team.yml',
            extravars={
                'art_branch': self.config['art_branch'],
                'art_repository': self.config['art_repository'],
                'run_specific_atomic_tests': run_specific_atomic_tests,
                'art_run_tests': simulation_atomics,
                'art_run_techniques': simulation_techniques,
                'ansible_user': 'Vagrant',
                'ansible_password': 'vagrant',
                'ansible_port': 5985,
                'ansible_winrm_scheme': 'http'
            },
            verbosity=0
        )

        if runner.status == "successful":
            self.log.info("successfully executed technique ID {0} against target: {1}".format(simulation_techniques, target))
        else:
            self.log.error("failed to executed technique ID {0} against target: {1}".format(simulation_techniques, target))
            sys.exit(1)

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

    def dump(self, dump_name):
        self.log.info("Dump log data")

        folder = "attack_data/" + dump_name
        os.mkdir(os.path.join(os.path.dirname(__file__), '../' + folder))


        with open(os.path.join(os.path.dirname(__file__), '../attack_data/dumps.yml')) as dumps:
            for dump in yaml.full_load(dumps):
                if dump['enabled']:
                    dump_out = dump['dump_parameters']['out']
                    dump_search = "search %s earliest=%s | sort 0 _time" \
                                  % (dump['dump_parameters']['search'], dump['dump_parameters']['time'])
                    dump_info = "Dumping Splunk Search to %s " % dump_out
                    self.log.info(dump_info)
                    out = open(os.path.join(os.path.dirname(__file__), "../attack_data/" + dump_name + "/" + dump_out), 'wb')
                    splunk_sdk.export_search(self.config['splunk_server_private_ip'],
                                             s=dump_search,
                                             password=self.config['splunk_admin_password'],
                                             out=out)
                    out.close()
                    self.log.info("%s [Completed]" % dump_info)