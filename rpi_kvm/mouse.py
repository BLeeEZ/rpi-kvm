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


class KvmMouse(object):
    def __init__(self):
        self.event_mice = dict()

    async def start(self):
        logging.info(f"D-Bus service connecting...")
        await self._connect_to_dbus_service()

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
                logging.info(f"D-Bus service connected")
            except dbus_next.DBusError:
                logging.warning(f"D-Bus service not available - reconnecting...")
                await asyncio.sleep(5)

    async def send_state(self, buttons, x_pos, y_pos, v_wheel, h_wheel):
        common_buttons = [False, False, False, False, False, False, False, False]
        for event_mouse in self.event_mice.values():
            for i, button_val in enumerate(event_mouse.buttons):
                common_buttons[i] |= button_val

        try:
            await self._kvm_dbus_iface.call_send_mouse_usb_telegram(common_buttons, x_pos, y_pos, v_wheel, h_wheel)
        except dbus_next.DBusError:
            logging.warning(f"{self._idev.path}: D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()


class EventMouse(object):
    def __init__(self, input_device):
        self._idev = input_device
        logging.info(f"{self._idev.path}: Init Mouse - {self._idev.name}")
        self.send_state_cb = None
        self.__client_switch_button_index = 2
        self._is_alive = False

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

    @property
    def is_alive(self):
        return self._is_alive

    @property
    def path(self):
        return self._idev.path

    @property
    def name(self):
        return self._idev.name

    @property
    def buttons(self):
        return self._buttons

    async def run(self):
        self._is_alive = True
        logging.info(f"{self._idev.path}: Start sending mouse sync events continuously")
        asyncio.create_task(self._continuous_sync_event())
        logging.info(f"{self._idev.path}: Start listening to mouse event loop")
        try:
            await self._event_loop()
        except Exception as e:
            logging.error(f"{self._idev.path}: {e}")
        self._is_alive = False

    # poll for mouse events
    async def _event_loop(self):
        async for event in self._idev.async_read_loop():
            await self._handle_event(event)

    # continuous mouse sync event to prevent input lag on host
    async def _continuous_sync_event(self):
        while self._is_alive:
            time_ns = time.time_ns()
            time_s = int(time_ns / 1_000_000_000)
            time_ms = int((time_ns - (time_s * 1_000_000_000)) / 1_000)
            # InputEvent.__init__(self, sec, usec, type, code, value)
             # code and value are chosen at random
            basic_event = evdev.events.InputEvent(time_s, time_ms, ecodes.EV_SYN, 55, 55)
            await self._handle_event(basic_event)
            await asyncio.sleep(1)

    async def _handle_event(self, event):
        if event.type == ecodes.EV_SYN:
            current_time = time.monotonic()
            if current_time - self._last_syn_event_time < self._update_rate and not self._have_buttons_changed:
                return
            self._last_syn_event_time = current_time
            if self.send_state_cb:
                await self.send_state_cb(self._buttons, self._x_pos, self._y_pos, self._v_wheel, self._h_wheel)
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
                    logging.debug(f"{self._idev.path}: Key event {ecodes.BTN[event.code]}: {event.value}")
                else:
                    logging.debug(f"{self._idev.path}: Key event {event.code}: {event.value}")
            elif event.code == 125: # MX Master 3 - Gesture mouse button
                logging.debug(f"{self._idev.path}: Key event BTN_GESTURE: {event.value}")
                self._have_buttons_changed = True
                self._buttons[self.__client_switch_button_index] = (event.value == 1)

        elif event.type == ecodes.EV_REL:
            if event.code == 0:
                self._x_pos += event.value
            elif event.code == 1:
                self._y_pos += event.value
            elif event.code == 8:
                logging.debug(f"{self._idev.path}: V-Wheel movement: {event.value}")
                self._v_wheel += event.value
            elif event.code == 6:
                logging.debug(f"{self._idev.path}: H-Wheel movement: {event.value}")
                self._h_wheel -= event.value

async def main():
    logging.basicConfig(format='Mouse %(levelname)s: %(message)s', level=logging.DEBUG)
    logging.info("Creating HID Manager")
    hid_manager = HidScanner()
    kvm_mouse = KvmMouse()
    await kvm_mouse.start()

    while True:
        await hid_manager.scan()

        removed_event_mice = [event_mouse for event_mouse in kvm_mouse.event_mice.values() if not event_mouse.is_alive]
        for event_mouse in removed_event_mice:
            logging.info(f"Removing event mouse: {event_mouse.path}")
            del kvm_mouse.event_mice[event_mouse.path]

        device_paths = [mouse_device.path for mouse_device in hid_manager.mouse_devices]
        if len(device_paths) == 0:
            logging.warning("No mouse device found, waiting till next device scan")
        else:
            new_device_mice = [mouse_device for mouse_device in hid_manager.mouse_devices if mouse_device.path not in kvm_mouse.event_mice]
            for mouse_device in new_device_mice:
                event_mouse = EventMouse(mouse_device)
                event_mouse.send_state_cb = kvm_mouse.send_state
                kvm_mouse.event_mice[mouse_device.path] = event_mouse
                asyncio.create_task(event_mouse.run())
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run( main() )
