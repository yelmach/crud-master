require 'yaml'

# 1. Load Infrastructure Config
CONFIG_FILE = File.expand_path("config.yaml", __dir__)
abort "Missing config.yaml file" unless File.file?(CONFIG_FILE)
infra = YAML.load_file(CONFIG_FILE)

# 2. Load Application Secrets
ENV_FILE = File.expand_path(".env", __dir__)
abort "Missing .env file at #{ENV_FILE}" unless File.file?(ENV_FILE)

env_vars = {}
File.readlines(ENV_FILE).each do |line|
  next if line.strip.empty? || line.start_with?('#')
  key, value = line.strip.split('=', 2)
  env_vars[key] = value if key && value
end

Vagrant.configure("2") do |config|
  # --- INVENTORY VM ---
  config.vm.define "inventory-vm" do |inventory|
    inventory.vm.box = "ubuntu/jammy64"
    inventory.vm.hostname = infra['inventory_vm']

    inventory.vm.network "private_network", ip: infra['inventory_vm_addr']
    inventory.vm.network "forwarded_port",
      guest: env_vars["INVENTORY_PORT"].to_i,
      host: env_vars["INVENTORY_PORT"].to_i

    inventory.vm.synced_folder infra['inventory_app_src'], infra['inventory_app_path'], type: "virtualbox"

    inventory.vm.provider "virtualbox" do |vb|
      vb.name = infra['inventory_vm']
      vb.memory = infra['inventory_vm_memory']
      vb.cpus = infra['inventory_vm_cpu']
    end

    inventory.vm.provision "shell",
      path: "scripts/setup_inventory.sh",
      env: env_vars,
      sensitive: true
  end

  # --- BILLING VM ---
  config.vm.define "billing-vm" do |billing|
		billing.vm.box = "ubuntu/jammy64"
		billing.vm.hostname = infra['billing_vm']
    
		billing.vm.network "private_network", ip: infra['billing_vm_addr']
		billing.vm.network "forwarded_port",
      guest: env_vars["BILLING_PORT"].to_i,
      host: env_vars["BILLING_PORT"].to_i

		billing.vm.synced_folder infra['billing_app_src'], infra['billing_app_path'], type: "virtualbox"

		billing.vm.provider "virtualbox" do |vb|
      vb.name = infra['billing_vm']
      vb.memory = infra['billing_vm_memory']
      vb.cpus = infra['billing_vm_cpu']
    end

    billing.vm.provision "shell",
      path: "scripts/setup_billing.sh",
      env: env_vars,
      sensitive: true
	end

  # --- GATEWAY VM ---
  config.vm.define "gateway-vm" do |gateway|
    gateway.vm.box = "ubuntu/jammy64"
    gateway.vm.hostname = infra['gateway_vm']

    gateway.vm.network "private_network", ip: infra['gateway_vm_addr']
    gateway.vm.network "forwarded_port",
      guest: env_vars["GATEWAY_PORT"].to_i,
      host: env_vars["GATEWAY_PORT"].to_i

    gateway.vm.synced_folder infra['gateway_app_src'], infra['gateway_app_path'], type: "virtualbox"

    gateway.vm.provider "virtualbox" do |vb|
      vb.name = infra['gateway_vm']
      vb.memory = infra['gateway_vm_memory']
      vb.cpus = infra['gateway_vm_cpu']
    end

    gateway.vm.provision "shell",
      path: "scripts/setup_gateway.sh",
      env: env_vars,
      sensitive: true
  end
end
