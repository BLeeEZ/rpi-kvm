#!/bin/bash

export RPI_KVM_PATH=$(pwd)

initRpiKvmTmux()
{
    tmux new-session -s rpi-kvm -n kvm -d

    tmux split-window -h -t rpi-kvm
    tmux split-window -v -t rpi-kvm
	tmux select-pane -t rpi-kvm:kvm.1
    tmux split-window -v -t rpi-kvm
	tmux select-pane -t rpi-kvm:kvm.3
    tmux split-window -v -t rpi-kvm

    tmux send-keys -t rpi-kvm:kvm.0 'cd $RPI_KVM_PATH && reset && sudo ./rpi_kvm/kvm_service.py' C-m
    tmux send-keys -t rpi-kvm:kvm.1 'cd $RPI_KVM_PATH && reset && ./rpi_kvm/web.py' C-m
    tmux send-keys -t rpi-kvm:kvm.2 'cd $RPI_KVM_PATH && reset && ./rpi_kvm/info_hub.py' C-m
    tmux send-keys -t rpi-kvm:kvm.3 'cd $RPI_KVM_PATH && reset && ./rpi_kvm/mouse.py' C-m
    tmux send-keys -t rpi-kvm:kvm.4 'cd $RPI_KVM_PATH && reset && ./rpi_kvm/keyboard.py' C-m

	tmux select-pane -t rpi-kvm:kvm.0
}

tmux has-session -t rpi-kvm 2>/dev/null

# Tmux session does not exist -> Create one
if [ $? != 0 ]; then
    initRpiKvmTmux
fi
