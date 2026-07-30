Vagrant.configure("2") do |config|
	config.vm.define "billing-vm" do |billing|
		billing.vm.box = "ubuntu/jammy64"
		billing.vm.hostname = "billing-vm"
		billing.vm.network "private_network", ip: "192.168.56.12"
		billing.vm.network "forwarded_port", guest: 5001, host: 5001, auto_correct: true

		billing.vm.synced_folder ".", "/vagrant", type: "virtualbox"

		billing.vm.provider "virtualbox" do |vb|
			vb.name = "billing-vm"
			vb.memory = 2048
			vb.cpus = 2
		end

		billing.vm.provision "shell", path: "scripts/setup_billing.sh", privileged: true
	end
end
ENV_FILE = File.expand_path(".env", __dir__)

abort "Missing .env file at #{ENV_FILE}" unless File.file?(ENV_FILE)

# Parse the .env file
env_vars = {}
File.readlines(ENV_FILE).each do |line|
  next if line.strip.empty? || line.start_with?('#')

  key, value = line.strip.split('=', 2)
  env_vars[key] = value if key && value
end

Vagrant.configure("2") do |config|
  config.vm.define "inventory-vm" do |inventory|
    inventory.vm.box = "ubuntu/jammy64"
    inventory.vm.hostname = "inventory-vm"

    inventory.vm.network "private_network", ip: "192.168.56.11"
    inventory.vm.network "forwarded_port",
      guest: env_vars["INVENTORY_PORT"].to_i,
      host: env_vars["INVENTORY_PORT"].to_i,
      host_ip: "127.0.0.1"

    inventory.vm.provider "virtualbox" do |virtualbox|
      virtualbox.name = "crud-master-inventory"
      virtualbox.memory = 1024
      virtualbox.cpus = 1
    end

    inventory.vm.provision "shell",
      path: "scripts/setup_inventory.sh",
      env: env_vars,
      sensitive: true
  end

  config.vm.define "gateway-vm" do |gateway|
    gateway.vm.box = "ubuntu/jammy64"
    gateway.vm.hostname = "gateway-vm"

    gateway.vm.network "private_network", ip: "192.168.56.10"
    gateway.vm.network "forwarded_port",
      guest: env_vars["GATEWAY_PORT"].to_i,
      host: env_vars["GATEWAY_PORT"].to_i,
      host_ip: "127.0.0.1"

    gateway.vm.provider "virtualbox" do |virtualbox|
      virtualbox.name = "crud-master-gateway"
      virtualbox.memory = 1024
      virtualbox.cpus = 1
    end

    gateway.vm.provision "shell",
      path: "scripts/setup_gateway.sh",
      env: env_vars,
      sensitive: true
  end
end
