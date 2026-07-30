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
end
