# based on https://github.com/jborean93/ansible-windows/blob/master/vagrant/Vagrantfile
require 'yaml'

inventory = YAML.load_file('inventory.yml')

vars = inventory['all']['vars']

# this idea stolen from here https://stackoverflow.com/a/53842768/6840572
ansible_provider = ''

Vagrant.configure("2") do |config|
  inventory['all']['hosts'].each do |host,details|
    config.vm.define host do |config|
      host_portion = details['ip'].split(/\./)[3].to_i
      config.vm.box = details['vagrant_box']
      config.vm.box_version = details['box_version'] if details.key?('box_version')
      config.vm.box_check_update = false # we specifically set the version for most of them so it's stable
      config.vm.hostname = host
      config.vbguest.auto_update = false # we can enable this later, but it just slows things down for now
      config.vm.synced_folder '.', '/vagrant', disabled: true

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

      config.vm.provider :virtualbox do |vb|
        ansible_provider = 'virtualbox'
        vb.gui = true # always have a GUI
        vb.name = 'RedTeamAttackLab_' + host
        vb.linked_clone = details.key?('linked_clone') ? details['linked_clone']: false
        vb.customize ["modifyvm", :id, "--memory", details.key?('memory') ? details['memory']: vars['default_host']['memory']]
        vb.customize ["modifyvm", :id, "--cpus", details.key?('cpus') ? details['cpus']: vars['default_host']['cpus']]
        vb.customize ["modifyvm", :id, "--vram", "32"]
        vb.customize ["modifyvm", :id, "--clipboard", "bidirectional"]
        vb.customize ["setextradata", "global", "GUI/SuppressMessages", "all" ]
      end

      # https://www.vagrantup.com/docs/providers/vmware/installation
      # https://www.vagrantup.com/vmware/downloads
      # NOT WORKING WITH WSL! the vmware-utility driver isn't working with wsl2!

      # Windows?
      # vagrant plugin install vagrant-vmware-desktop
      # net.exe start vagrant-vmware-utility
      config.vm.provider :vmware_desktop do |vmware_desktop|
        ansible_provider = 'vmware_desktop'

        vmware_desktop.gui = true
        vmware_desktop.linked_clone = details.key?('linked_clone') ? details['linked_clone']: false
        vmware_desktop.vmx["memsize"] = details.key?('memory') ? details['memory']: vars['default_host']['memory']
        vmware_desktop.vmx["numvcpus"] = details.key?('cpus') ? details['cpus']: vars['default_host']['cpus']
      end

      config.vm.provider :vmware_esxi do |esxi|
        ansible_provider = 'vmware_esxi'
        #  REQUIRED!  ESXi hostname/IP
        esxi.esxi_hostname = '192.168.1.12' # testing IP, change this!
        #  ESXi username
        esxi.esxi_username = 'vagrant' # example username, set this to what it is on your esxi host
        #  IMPORTANT!  Set ESXi password.
        #    1) 'prompt:'
        #    2) 'file:'  or  'file:my_secret_file'
        #    3) 'env:'  or 'env:my_secret_env_var'
        #    4) 'key:'  or  key:~/.ssh/some_ssh_private_key'
        #    5) or esxi.esxi_password = 'my_esxi_password'
        esxi.esxi_password = 'SpinThemUp!' # testing password, set this to be strong!

        #  HIGHLY RECOMMENDED!  ESXi Virtual Network
        #    You should specify an ESXi Virtual Network!  If it's not specified, the
        #    default is to use the first found.  You can specify up to 10 virtual
        #    networks using an array format.
        #esxi.esxi_virtual_network = ['VM Network','VM Network2','VM Network3','VM Network4']
        # the first one needs to be the management interface, so not some esxi-host-only interface!
        # set the second one to YOUR named network!
        esxi.esxi_virtual_network = ['LAN', 'Red Team Attack Lab']

        #  OPTIONAL.  Specify a Disk Store
        # set this to YOUR esxi drive
        esxi.esxi_disk_store = 'SSD Primary'

        #  OPTIONAL.  Guest VM name to use.
        #    The Default will be automatically generated.
        esxi.guest_name = 'RedTeamAttackLab_' + host

        #  OPTIONAL.  Memory size override
        esxi.guest_memsize = details['memory'] || vars['default_host']['memory']

        #  OPTIONAL.  Virtual CPUs override
        esxi.guest_numvcpus = details['cpus'] || vars['default_host']['cpus']
      end

      # it doesn't matter if we send extra variables for windows hosts to linux boxes
      config.vm.provision "ansible" do |ansible|
        # if we're using esxi, we don't want Ansible hitting the port forwarded port, we want the normal comm port
        if ansible_provider == 'vmware_esxi'
          if details['box_type'] == 'linux'
            ansible_port = 22
          else # windows
            ansible_port = 5985
          end
        end
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
    end
  end
end