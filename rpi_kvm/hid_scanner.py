#!/usr/bin/python3

import asyncio
import evdev
import logging

class HidScanner(object):
    def __init__(self):
        self._devices = []
        self._keyboards = []
        self._mice = []

    @property
    def devices(self):
        return self._devices

    @property
    def keyboard_devices(self):
        return self._keyboards

    @property
    def mouse_devices(self):
        return self._mice

    async def scan(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._scan_for_devices_via_blocking_evdev)
    
    def _scan_for_devices_via_blocking_evdev(self):
        self._devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        self._keyboards = []
        self._mice = []
        for device in self._devices:
            # has device a right button -> it's a mouse
            if evdev.ecodes.BTN_RIGHT in device.capabilities().get(evdev.ecodes.EV_KEY, []):
                self._mice.append(device)
            else:
                self._keyboards.append(device)

    def info(self, verbose=False):
        logging.info(f"=== devices ========================")
        for device in self._devices:
            logging.info(f"{device.path} {device.name} {device.phys}")
            if verbose:
                logging.info(f"{device.capabilities(verbose=True)}")
                logging.info(f"-----------------------------------")
        logging.info(f"=== keyboards ======================")
        for device in self._keyboards:
            logging.info(f"{device.path} {device.name} {device.phys}")
        logging.info(f"=== mice ===========================")
        for device in self._mice:
            logging.info(f"{device.path} {device.name} {device.phys}")

async def main():
    logging.basicConfig(format='HID %(levelname)s: %(message)s', level=logging.DEBUG)
    hid_manager = HidScanner()
    await hid_manager.scan()
    hid_manager.info()

if __name__ == "__main__":
    asyncio.run( main() )
