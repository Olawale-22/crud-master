Vagrant.configure("2") do |config|
  config.vm.boot_timeout = 600  # Increase the timeout to 10 minutes

  # Sync the scripts folder to all VMs
  config.vm.synced_folder "./scripts", "/vagrant/scripts"

  # Gateway VM for API gateway
  config.vm.define "gateway-vm" do |gateway|
    gateway.vm.box = "generic/ubuntu2204"
    gateway.vm.hostname = "api-gateway"
    gateway.vm.network "private_network", ip: "192.168.56.22"
    gateway.vm.network "forwarded_port", guest: 8000, host: 8002
  
    # Sync API gateway folder
    gateway.vm.synced_folder "./srcs/api-gateway", "/vagrant/srcs/api-gateway"
    gateway.vm.provision "shell", inline: <<-SHELL
      chmod +x /vagrant/scripts/setup_gateway.sh
      chmod +x /vagrant/scripts/start_services.sh
    SHELL
    gateway.vm.provision "shell", path: "scripts/setup_gateway.sh"
    gateway.vm.provision "shell", path: "scripts/start_services.sh", privileged: false
  
    gateway.vm.provider "virtualbox" do |vb|
      vb.memory = "1024"
    end
  end

  # Inventory VM for Inventory API and movies_db
  config.vm.define "inventory-vm" do |inventory|
    inventory.vm.box = "generic/ubuntu2204"
    inventory.vm.hostname = "inventory-app"
    inventory.vm.network "private_network", ip: "192.168.56.23"
    inventory.vm.network "forwarded_port", guest: 5014, host: 5003

    # Sync Inventory folder
    inventory.vm.synced_folder "./srcs/inventory-app", "/vagrant/srcs/inventory-app"
    inventory.vm.provision "shell", inline: <<-SHELL
      chmod +x /vagrant/scripts/setup_inventory.sh
      chmod +x /vagrant/scripts/start_services.sh
      chmod +x /vagrant/scripts/setup_services.sh
    SHELL
    inventory.vm.provision "shell", path: "scripts/setup_inventory.sh"
    inventory.vm.provision "shell", path: "scripts/start_services.sh", privileged: false

    # Run the setup_services.sh script for postgresql user permissions
    inventory.vm.provision "shell", path: "scripts/setup_services.sh", privileged: true

    inventory.vm.provider "virtualbox" do |vb|
      vb.memory = "1024"
    end
  end

  # Billing VM for Billing API and RabbitMQ
  config.vm.define "billing-vm" do |billing|
    billing.vm.box = "generic/ubuntu2204"
    billing.vm.hostname = "billing-app"
    billing.vm.network "private_network", ip: "192.168.56.24"
    billing.vm.network "forwarded_port", guest: 5008, host: 5004
  
    # Sync Billing folder
    billing.vm.synced_folder "./srcs/billing-app", "/vagrant/srcs/billing-app"
    billing.vm.provision "shell", inline: <<-SHELL
      chmod +x /vagrant/scripts/setup_billing.sh
      chmod +x /vagrant/scripts/start_services.sh
      chmod +x /vagrant/scripts/setup_services.sh
    SHELL
    billing.vm.provision "shell", path: "scripts/setup_billing.sh"
    billing.vm.provision "shell", path: "scripts/start_services.sh", privileged: false

    # Run the setup_services.sh script for postgresql and rabbitmq permissions and privileges
    billing.vm.provision "shell", path: "scripts/setup_services.sh", privileged: true

    billing.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
    end
  end
end