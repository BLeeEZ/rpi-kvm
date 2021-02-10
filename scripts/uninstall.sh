#!/bin/bash

echo "### RPI-KVM Uninstall ############"
if [ -f "./conf/bluetooth.service.bak" ] ; then
    echo "Restore bluetooth service config backup"
    sudo cp ./conf/bluetooth.service.bak /lib/systemd/system/bluetooth.service
    sudo systemctl daemon-reload
    echo "Restart bluetooth with the original config"
    sudo systemctl restart bluetooth
fi
if [ -f "/lib/systemd/system/rpi-kvm.service" ] ; then
    echo "Stop RPI-KVM service"
    sudo systemctl stop rpi-kvm
    echo "Disable RPI-KVM service"
    sudo systemctl disable rpi-kvm
    echo "Remove RPI-KVM service"
    sudo rm /lib/systemd/system/rpi-kvm.service
    sudo systemctl daemon-reload
fi
if [ -f "/etc/dbus-1/system.d/org.rpi.kvmservice.conf" ] ; then
    echo "Remove RPI-KVM D-Bus config"
    sudo rm /etc/dbus-1/system.d/org.rpi.kvmservice.conf
fi
echo "### RPI-KVM Uninstall Done #######"
