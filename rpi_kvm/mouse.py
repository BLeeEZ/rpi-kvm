#!/usr/bin/python3

import asyncio
import evdev
from evdev import *
import dbus_next
from dbus_next.aio import MessageBus
import time
import logging
from hid_scanner import HidScanner
from usb_hid_decoder import UsbHidDecoder

class Mouse(object):
    def __init__(self, input_device):
        self._idev = input_device
        logging.info(f"{self._idev.path}: Init Mouse - {self._idev.name}")
        self.__client_switch_button_index = 2
        self._buttons = [ # One byte size (bit map) to represent the mouse buttons
            False, # USB not defined
            False, # USB not defined
            False, # USB not defined. Not send via bluetooth -> placeholder for client switch
            False, # Forward mouse button
            False, # Backward mouse button
            False, # Middle mouse button
            False, # Right mouse button
            False] # Left mouse button
        self._x_pos = 0
        self._y_pos = 0
        self._v_wheel = 0
        self._h_wheel = 0
        self._have_buttons_changed = False
        self._last_syn_event_time = 0
        self._update_rate = 20/1000

    async def run(self):
        logging.info(f"{self._idev.path}: D-Bus service connecting...")
        await self._connect_to_dbus_service()
        logging.info(f"{self._idev.path}: Start sending mouse sync events continuously")
        asyncio.create_task(self._continuous_sync_event())
        logging.info(f"{self._idev.path}: Start listening to mouse event loop")
        await self._event_loop()

    # poll for mouse events
    async def _event_loop(self):
        async for event in self._idev.async_read_loop():
            await self._handle_event(event)

    # continuous mouse sync event to prevent input lag on host
    async def _continuous_sync_event(self):
        while True:
            time_ns = time.time_ns()
            time_s = int(time_ns / 1_000_000_000)
            time_ms = int((time_ns - (time_s * 1_000_000_000)) / 1_000)
            # InputEvent.__init__(self, sec, usec, type, code, value)
             # code and value are chosen at random
            basic_event = evdev.events.InputEvent(time_s, time_ms, ecodes.EV_SYN, 55, 55)
            await self._handle_event(basic_event)
            await asyncio.sleep(1)

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
        try:
            await self._kvm_dbus_iface.call_send_mouse_usb_telegram(self._buttons, self._x_pos, self._y_pos, self._v_wheel, self._h_wheel)
        except dbus_next.DBusError:
            logging.warning(f"{self._idev.path}: D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()

    async def _handle_event(self, event):
        if event.type == ecodes.EV_SYN:
            current_time = time.monotonic()
            if current_time - self._last_syn_event_time < self._update_rate and not self._have_buttons_changed:
                return
            self._last_syn_event_time = current_time
            await self._send_state()
            self._x_pos = 0
            self._y_pos = 0
            self._v_wheel = 0
            self._h_wheel = 0
            self._have_buttons_changed = False
        elif event.type == ecodes.EV_KEY:
            button_index = UsbHidDecoder.encode_mouse_button_index(event.code)
            if button_index >= 0 and event.value < 2:
                self._have_buttons_changed = True
                self._buttons[button_index] = (event.value == 1)
                if event.code in ecodes.BTN:
                    logging.debug(f"Key event {ecodes.BTN[event.code]}: {event.value}")
                else:
                    logging.debug(f"Key event {event.code}: {event.value}")
            elif event.code == 125: # MX Master 3 - Gesture mouse button
                logging.debug(f"Key event BTN_GESTURE: {event.value}")
                self._have_buttons_changed = True
                self._buttons[self.__client_switch_button_index] = (event.value == 1)

        elif event.type == ecodes.EV_REL:
            if event.code == 0:
                self._x_pos += event.value
            elif event.code == 1:
                self._y_pos += event.value
            elif event.code == 8:
                logging.debug(f"V-Wheel movement: {event.value}")
                self._v_wheel += event.value
            elif event.code == 6:
                logging.debug(f"H-Wheel movement: {event.value}")
                self._h_wheel -= event.value

async def main():
    logging.basicConfig(format='Mouse %(levelname)s: %(message)s', level=logging.DEBUG)
    logging.info("Creating HID Manager")
    hid_manager = HidScanner()
    hid_manager.scan()

    while len(hid_manager.mouse_devices) == 0:
        logging.warning("No mouse found, waiting 3 seconds and retrying")
        asyncio.sleep(3)
    
    for mouse_device in hid_manager.mouse_devices:
        mouse = Mouse(mouse_device)
        asyncio.create_task(mouse.run())
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run( main() )
