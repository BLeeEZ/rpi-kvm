# Raspberry Pi USB - Bluetooth K(V)M

## Getting started

### Step 1: Install

Connect to your raspberry pi via ssh:

``` bash
cd /home/pi
git clone https://github.com/BLeeEZ/rpi-kvm.git
cd rpi-kvm
sudo ./rpi-kvm.sh install
```

### Step 2: Start the RPI-K(V)M service

``` bash
sudo ./rpi-kvm.sh start
```

### Step 3: Optional steps

#### a) Display status and additional information

RPI-K(V)M is running in a tmux session. To see the service logger messages:

``` bash
sudo ./rpi-kvm.sh attach
```

#### b) Open the web interface

To see detailed bluetooth client information go the RPI-K(V)M web interface: [http://raspberrypi:8080](http://raspberrypi:8080)
>Note: If the host name has been changed during inital Raspberry Pi setup the webserver is reachable at its new RPI-KVM host name or its IP address

#### c) Connect a HD44780 LCD display

Follow [this](/docu/lcd.md) wiring guide to display the bluetooth clients on a LCD display.

![Animated lcd display bluetooth client switch](/.github/Screenshots/lcd.gif)

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