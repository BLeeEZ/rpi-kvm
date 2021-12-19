#! /bin/bash

echo "### RPI-KVM Install ##############"
echo "--- RPI-KVM Dependency Install ---"
echo "Install required basic packages via apt-get"
sudo apt-get install git tmux python python3 python-dev python3-dev python3-pip -y
echo "Install required bluetooth packages via apt-get"
sudo apt-get install bluez bluez-tools bluez-firmware python-bluez -y
echo "Install required python packages via pip3"
sudo pip3 install evdev dbus-next aiohttp RPi.GPIO
echo "Install required python packages via apt-get"
sudo apt-get install python3-pyudev python3-evdev python3-dbus python3-numpy python3-gi -y
echo "Install dev tools"
curl -sSL https://deb.nodesource.com/setup_16.x | sudo bash -
sudo apt install -y nodejs
echo "--- Dependency Install Done ------"

echo "--- RPI-KVM Configuration Step ---"
echo "Copy RPI-KVM D-Bus config"
sudo cp ./conf/org.rpi.kvmservice.conf /etc/dbus-1/system.d/
echo "Create backup of the current bluetooth service config"
sudo cp /lib/systemd/system/bluetooth.service ./conf/bluetooth.service.bak
echo "Copy RPI-KVM bluetooth service config"
# The RPI-KVM bluetooth service config deactivates the 'input' plugin.
# For RPI-KVM to accept connections it is neccessary to disable the Bluez 'input' plugin by 
# adding the arg "--noplugin=input" to 'ExecStart' command in the bluetooth.service
# The ports we have to use to emulated the keyboard and mouse are ports reserved for
# Bluetooth human interface devices.
# The 'input' plugin handles those devices and the ports are taken
# if the input plugin is enabled.
# Remark: Other bluetooth input devices can't be connected,
# if the 'input' plugin is disabled.
sudo cp ./conf/bluetooth.service /lib/systemd/system/bluetooth.service
echo "Copy RPI-KVM service config"
sudo cp ./conf/rpi-kvm.service /lib/systemd/system/rpi-kvm.service
sudo systemctl daemon-reload
echo "Restart bluetooth service with the new config"
sudo systemctl restart bluetooth
echo "Enable RPI-KVM service"
sudo systemctl enable rpi-kvm
echo "Start RPI-KVM service"
sudo systemctl start rpi-kvm
echo "--- Configuration Step Done ------"
echo "### RPI-KVM Install Done #########"
