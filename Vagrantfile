# based on https://github.com/jborean93/ansible-windows/blob/master/vagrant/Vagrantfile
require 'yaml'

inventory = YAML.load_file('inventory.yml')

vars = inventory['all']['vars']

Vagrant.configure("2") do |config|
  inventory['all']['hosts'].each do |host,details|
    config.vm.define host do |config|
      host_portion = details['ip'].split(/\./)[3].to_i
      config.vm.box = details['vagrant_box']
      config.vm.box_version = details['box_version'] if details.key?('box_version')
      config.vm.box_check_update = false # we specifically set the version for most of them so it's stable
      config.vm.hostname = host
      config.vbguest.auto_update = false # we can enable this later, but it just slows things down for now

      if details['box_type'] == 'linux'
        ansible_port = vars['vagrant_ports']['ssh']['host'] + host_portion
      else # default to windows hosts
        ansible_port = vars['vagrant_ports']['winrm_http']['host'] + host_portion
        config.vm.guest = :windows # it was working fine without this, but might as well add it
        config.vm.communicator = "winrm"
        config.vm.boot_timeout = 600 # might need to increase this per issue 2... wasn't happening before though
        config.winrm.timeout = 300 # might need to remove/increase this per issue 2
        config.winrm.basic_auth_only = true # we should be able to remove this
        config.winrm.retry_limit = 20 # not sure if this does anything, should be able to remove
      end

      config.vm.network :private_network, ip: details['ip']
      vars['vagrant_ports'].each do |protocol, details|
        config.vm.network :forwarded_port, guest: details['guest'], host: details['host'] + host_portion
      end

      config.vm.synced_folder '.', '/vagrant', disabled: true

      # it doesn't matter if we send extra variables for windows hosts to linux boxes
      config.vm.provision "ansible" do |ansible|
        ansible.extra_vars = {
          ansible_port: ansible_port,
          ansible_winrm_scheme: vars['ansible_winrm_scheme'],
          ansible_winrm_server_cert_validation: vars['ansible_winrm_server_cert_validation'],
          win_password: vars['win_domain_admin_pass'],
          windows_domain_controller_private_ip: inventory['all']['hosts']['dc01']['ip'],
          win_timezone: vars['win_timezone'],
          root_domain: vars['root_domain'],
          domain_name: vars['domain_name'],
          win_domain_admin: vars['win_domain_admin'],
          local_admin_password: vars['local_admin_password'],
          hostname: config.vm.hostname
        }
        ansible.playbook = "ansible/#{host}.yml"
        ansible.config_file = "ansible/ansible.cfg"
        ansible.compatibility_mode = "2.0"
      end

      config.vm.provider :virtualbox do |vb|
        vb.gui = true # always have a GUI
        vb.name = 'RedTeamAttackLab_' + host
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