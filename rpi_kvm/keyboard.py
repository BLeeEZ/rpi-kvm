#!/usr/bin/python3

import asyncio
import evdev
from evdev import *
import dbus_next
from dbus_next.aio import MessageBus
import logging
from hid_scanner import HidScanner
from usb_hid_decoder import UsbHidDecoder

class Keyboard(object):
    def __init__(self, input_device):
        self._idev = input_device
        logging.info(f"{self._idev.path}: Init Keyboard - {self._idev.name}")
        self._modifiers = [ # One byte size (bit map) to represent the pressed modifier keys
            False, # Right GUI
            False, # Right Alt
            False, # Right Shift
            False, # Right Control
            False, # Left GUI
            False, # Left Alt
            False, # Left Shift
            False] # Left Control
        # Place for 6 simultaneously pressed regular keys
        self._keys = [
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00]

    async def run(self):
        logging.info(f"{self._idev.path}: D-Bus service connecting...")
        await self._connect_to_dbus_service()
        logging.info(f"{self._idev.path}: Starting event loop")
        await self._event_loop()

    # poll for keyboard events
    async def _event_loop(self):
        async for event in self._idev.async_read_loop():
            # only bother if we hit a key and its an up or down event
            if event.type == ecodes.EV_KEY and event.value < 2:
                self._handle_event(event)
                await self._send_state()

    async def _connect_to_dbus_service(self):
        self._kvm_dbus_iface = None
        while not self._kvm_dbus_iface:
            try:
                bus = await MessageBus(bus_type=dbus_next.BusType.SYSTEM).connect()
                introspection = await bus.introspect(
                    'org.rpi.kvmservice', '/org/rpi/kvmservice')
                kvm_service_obj = bus.get_proxy_object(
                    'org.rpi.kvmservice', '/org/rpi/kvmservice', introspection)
                self._kvm_dbus_iface = kvm_service_obj.get_interface('org.rpi.kvmservice')
                logging.info(f"{self._idev.path}: D-Bus service connected")
            except dbus_next.DBusError:
                logging.warning(f"{self._idev.path}: D-Bus service not available - reconnecting...")
                await asyncio.sleep(5)

    async def _send_state(self):
        modifier_str = ''
        for i in self._modifiers:
            mod_value_str = "1" if i else "0"
            modifier_str += mod_value_str
        logging.debug(f"{self._idev.path}: mod: {modifier_str} keys: {self._keys}")
        try:
            await self._kvm_dbus_iface.call_send_keyboard_usb_telegram(self._modifiers, bytes(self._keys))
        except dbus_next.DBusError:
            logging.warning(f"{self._idev.path}: D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()

    def _handle_event(self, event):
        if event.code not in ecodes.KEY:
            logging.warning(f"{self._idev.path}: unsupported key press code: {event.code}")
            return
        evdev_code = ecodes.KEY[event.code]
        if UsbHidDecoder.is_modifier_key(evdev_code):
            modifier_index = UsbHidDecoder.encode_modifier_key_index(evdev_code)
            self._modifiers[modifier_index] = not self._modifiers[modifier_index]
        else:
            usb_key_code = UsbHidDecoder.encode_regular_key(evdev_code)
            for i in range(0, 6):
                if self._keys[i] == usb_key_code and event.value == 0:
                    self._keys[i] = 0x00 # Code 0x00 represents a key release
                elif self._keys[i] == 0x00 and event.value == 1:
                    self._keys[i] = usb_key_code
                    break

async def main():
    logging.basicConfig(format='KB %(levelname)s: %(message)s', level=logging.DEBUG)
    logging.info("Creating HID Manager")
    hid_manager = HidScanner()
    hid_manager.scan()

    while len(hid_manager.keyboard_devices) == 0:
        logging.warning("No keyboard found, waiting 3 seconds and retrying")
        asyncio.sleep(3)
    
    for keyboard_device in hid_manager.keyboard_devices:
        kb = Keyboard(keyboard_device)
        asyncio.create_task(kb.run())
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run( main() )
