#!/bin/bash

case "$1" in
    install)
        sudo ./scripts/install.sh
        ;;
    uninstall)
        sudo ./scripts/uninstall.sh
        ;;
    debug)
        sudo ./rpi-kvm.sh restart
        sudo ./rpi-kvm.sh attach
        ;;
    attach)
        sudo tmux attach-session -t rpi-kvm
        ;;
    kill)
        sudo tmux kill-session -t rpi-kvm
        ;;
    start)
        sudo ./scripts/init.sh
        ;;
    restart)
        sudo tmux kill-session -t rpi-kvm
        sudo ./scripts/init.sh
        ;;
    update-mac)
        sudo ./scripts/update-mac.sh
        ;;
    update-name)
        sudo ./scripts/update-name.sh
        ;;
    *)
        echo "Incorrect input provided"
esac