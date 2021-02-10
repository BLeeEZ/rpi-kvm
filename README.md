# Raspberry Pi USB - Bluetooth K(V)M

## Getting started

### Step 1: Install

Connect to your raspberry pi via ssh.

``` bash
cd /home/pi
git clone https://github.com/BLeeEZ/rpi-kvm.git
cd rpi-kvm
sudo ./rpi-kvm.sh install
```

### Step 2: Start the K(V)M service

``` bash
sudo ./rpi-kvm.sh start
```

### Step 3: Display status and additianl information (optional)

The K(V)M is running in a tmux session. To see the service output:

``` bash
sudo ./rpi-kvm.sh attach
```

## Technologies

### Linux

- Tmux
- D-Bus
- Bluetooth (BLueZ)
- HD44780-LCD support (optional)

### Python

- asyncio
- evdev
- dbus_next
- aiohttp

### Web

- Bootstrap: https://getbootstrap.com/
- React Js: https://reactjs.org/
- Babel.js: In-browser Babel transformer for jsx to js