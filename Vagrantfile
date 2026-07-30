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
