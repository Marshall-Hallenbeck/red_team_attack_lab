require 'yaml'

inventory = YAML.load_file('inventory.yml')

vars = inventory['all']['vars']

Vagrant.configure("2") do |config|
  inventory['all']['hosts'].each do |server,details|
    host_portion = details['ip'].split(/\./)[3].to_i
    config.vm.define server do |srv|
      winrm_port = vars['vagrant_ports']['winrm_http']['host'] + host_portion
      srv.vm.box = details['vagrant_box']
      srv.vm.box_version = details['box_version'] if details.key?('box_version')
      srv.vm.hostname = server
      srv.vm.communicator = "winrm"
      srv.winrm.timeout = 300
      srv.vm.network :private_network, ip: details['ip']
      vars['vagrant_ports'].each do |protocol, details|
        srv.vm.network :forwarded_port, guest: details['guest'], host: details['host'] + host_portion
      end

      config.vm.provision "ansible" do |ansible|
        ansible.extra_vars = {
          ansible_port: winrm_port,
          ansible_winrm_scheme: 'http',
          win_password: vars['win_domain_admin_pass'],
          windows_domain_controller_private_ip: inventory['all']['hosts']['dc01']['ip'],
          win_timezone: vars['win_timezone'],
          root_domain: vars['root_domain'],
          domain_name: vars['domain_name'],
          win_domain_admin: vars['win_domain_admin'],
          local_admin_password: vars['local_admin_password']
        }
        ansible.playbook = "../ansible/#{server}.yml"
        ansible.config_file = "../ansible/ansible.cfg"
        ansible.compatibility_mode = "2.0"
      end

      srv.vm.provider :virtualbox do |vb|
        vb.gui = true # always have a GUI
        vb.name = 'RedTeamAttackLab_' + server
        vb.linked_clone = details.key?('linked_clone') ? details['linked_clone']: false
        vb.customize ["modifyvm", :id, "--memory", details.key?('memory') ? details['memory']: vars['default_host']['memory']]
        vb.customize ["modifyvm", :id, "--cpus", details.key?('cpus') ? details['cpus']: vars['default_host']['cpus']]
        vb.customize ["modifyvm", :id, "--vram", "32"]
        vb.customize ["modifyvm", :id, "--clipboard", "bidirectional"]
        vb.customize ["setextradata", "global", "GUI/SuppressMessages", "all" ]
      end
    end
  end
end