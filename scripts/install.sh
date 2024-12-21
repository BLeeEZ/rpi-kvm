#! /bin/bash

function fail {
	printf '%s\n' "$1" >&2 ## Send a message to stderr
	exit "${2-1}" 
}

echo "### RPI-KVM Install ##############"
echo "--- RPI-KVM Dependency Install ---"
echo "Install required basic packages via apt-get"
sudo apt update
sudo apt-get install git tmux python-is-python3 python3 python3-dev python3-pip -y
echo "Install required bluetooth packages via apt-get"
sudo apt-get install bluez bluez-tools bluez-firmware python3-bluez -y
echo "Install required python packages via apt-get"
sudo apt-get install python3-pyudev python3-evdev python3-dbus python3-dbus-next python3-aiohttp python3-rpi.gpio python3-numpy python3-gi -y
echo "Install nodejs"
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo mkdir -p /etc/apt/keyrings
# --yes allows overwriting if re-running the script (to repair a broken install or get new fixes)
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor --yes -o /etc/apt/keyrings/nodesource.gpg
# This can be changed to a newer supported version once tested
NODE_MAJOR=16
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
sudo apt-get update
sudo apt-get install nodejs -y
echo "--- Dependency Install Done ------"

echo "--- RPI-KVM Configuration Step ---"
echo "Copy RPI-KVM D-Bus config"
sudo cp ./conf/org.rpi.kvmservice.conf /etc/dbus-1/system.d/

if [ ! -f "./conf/bluetooth.service.bak" ]; then
	echo "Create backup of the current bluetooth service config"
	sudo cp /lib/systemd/system/bluetooth.service ./conf/bluetooth.service.bak
fi

if [ -f "/usr/lib/bluetooth/bluetoothd" ]; then
	bluetoothd_path="/usr/lib/bluetooth/bluetoothd"
elif [ -f "/usr/libexec/bluetooth/bluetoothd" ]; then
	bluetoothd_path="/usr/libexec/bluetooth/bluetoothd"
else
	fail "The bluetooth daemon path \"bluetoothd\" could't be found!"
fi
echo "The bluetooth daemon path for \"bluetoothd\" is: ${bluetoothd_path}"

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
# Replace the placeholder for the bluetooth daemon path with the correct path
sudo sed -i "s|BLUETOOTH_DAEMON_PATH|${bluetoothd_path}|" /lib/systemd/system/bluetooth.service

echo "Copy RPI-KVM service config"
sudo cp ./conf/rpi-kvm.service /lib/systemd/system/rpi-kvm.service
echo "Replace legacy pi user with current user if necessary"
sudo sed -i'' -e "s|/pi/|/${SUDO_USER}/|g" /lib/systemd/system/rpi-kvm.service
sudo systemctl daemon-reload
echo "Restart bluetooth service with the new config"
sudo systemctl restart bluetooth
echo "Enable RPI-KVM service"
sudo systemctl enable rpi-kvm
echo "Start RPI-KVM service"
sudo systemctl start rpi-kvm
echo "--- Configuration Step Done ------"
echo "### RPI-KVM Install Done #########"
