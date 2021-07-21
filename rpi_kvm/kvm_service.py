#!/usr/bin/python3
#
# Bluetooth D-Bus Service

import os
import sys
import asyncio
import dbus_next
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface
from dbus_next import Variant
import signal
import logging
import json
from settings import Settings
from bt_server import BtServer
from hotkey import HotkeyDetector, HotkeyConfig, HotkeyAktion
from usb_hid_decoder import UsbHidDecoder

class KvmDbusService(ServiceInterface):
    def __init__(self, settings, hotkey_detector, bt_server):
        super().__init__("org.rpi.kvmservice")
        self._settings = settings
        self._hotkey_detector = hotkey_detector
        self._bt_server = bt_server
        self._stop_event = False

    def stop(self):
        self._stop_event = True

    def on_clients_change(self, clients):
        self.signal_clients_change(clients)

    async def run(self):
        logging.info("D-Bus: Register D-Bus service")
        await self._register_to_dbus()
        logging.info("D-Bus: Register notifier on Bluetooth server: on client change")
        self._bt_server.register_on_clients_change_handler(self)
        logging.info("D-Bus: Run in loop")
        while not self._stop_event:
            await asyncio.sleep(2)
        logging.info("D-Bus: Unregister notifier on Bluetooth server: on client change")
        self._bt_server.unregister_on_clients_change_handler(self)
        logging.info("D-Bus: D-Bus service finished")

    async def _register_to_dbus(self):
        self._bus = await MessageBus(bus_type=dbus_next.BusType.SYSTEM).connect()
        self._bus.export("/org/rpi/kvmservice", self)
        await self._bus.request_name("org.rpi.kvmservice")

    @dbus_next.service.method()
    def GetConnectedClientNames(self) -> 'as':
        return self._bt_server.get_connected_client_names()

    @dbus_next.service.method()
    def GetClientsInfo(self) -> 's':
        return json.dumps(self._bt_server.get_clients_info_dict())

    @dbus_next.service.method()
    def ConnectClient(self, client_address: 's') -> '':
        self._bt_server.connect_client(client_address)
        return

    @dbus_next.service.method()
    def DisconnectClient(self, client_address: 's') -> '':
        self._bt_server.disconnect_client(client_address)
        return

    @dbus_next.service.method()
    def ReloadSettings(self) -> '':
        logging.info(f"D-Bus: Reload settings")
        self._hotkey_detector.reload_settings()
        return
    
    @dbus_next.service.method()
    def RestartInfoHub(self) -> '':
        logging.info(f"D-Bus: Restart Info Hub")
        self.signal_restart_info_hub()
        return

    @dbus_next.service.method()
    def SwitchActiveHost(self, client_address: 's') -> '':
        self._bt_server.switch_active_host_to(client_address)
        client_names = self._bt_server.get_connected_client_names()
        logging.info(f"D-Bus: Switch active host to: {client_names[0]}")
        self.signal_host_change(client_names)

    @dbus_next.service.method()
    def SendKeyboardUsbTelegram(self, modifiers: 'ab', keys: 'ay') -> '':
        modifiers_int =  UsbHidDecoder.convert_modifier_bit_mask_to_int(modifiers)
        action = self._hotkey_detector.evaluate_new_input([modifiers_int, *keys])
        # Only the last key of the hot key combination will not be sendted
        if action == HotkeyAktion.SwitchToNextHost:
            self._bt_server.switch_to_next_connected_host()
            client_names = self._bt_server.get_connected_client_names()
            logging.info(f"D-Bus: {action.name}: {client_names[0]}")
            self.signal_host_change(client_names)
        else:
            # |- USB HID input report
            # |     |- USB HID usage report => Keyboard
            # |     |     |- Bit mask for modifier keys
            # |     |     |  0x80: Right GUI
            # |     |     |  0x40: Right Alt
            # |     |     |  0x20: Right Shift
            # |     |     |  0x10: Right Control
            # |     |     |  0x08: Left GUI
            # |     |     |  0x04: Left Alt
            # |     |     |  0x02: Left Shift
            # |     |     |  0x01: Left Control
            # |     |     |     |- Vendor reserved
            # |     |     |     |     |-> 6x pressed keys
            # 0xA1, 0x01, 0xXX, 0x00, 0xXX, 0xXX, 0xXX, 0xXX, 0xXX, 0xXX
            keyboard_usb_telegram = [0xA1, 1, modifiers_int, 0, *keys]
            self._bt_server.send(keyboard_usb_telegram)

    @dbus_next.service.method()
    def SendMouseUsbTelegram(self, buttons: 'ab', x_pos: 'i', y_pos: 'i', v_wheel: 'i', h_wheel: 'i') -> '':
        buttons_byte = UsbHidDecoder.convert_modifier_bit_mask_to_int(buttons)
        # limit the values to fit inside 1 byte
        x_pos_byte = UsbHidDecoder.enshure_byte_size(x_pos)
        y_pos_byte = UsbHidDecoder.enshure_byte_size(y_pos)
        v_wheel_byte = UsbHidDecoder.enshure_byte_size(v_wheel)
        h_wheel_byte = UsbHidDecoder.enshure_byte_size(h_wheel)
        # |- USB HID input report
        # |     |- USB HID usage report => Mouse
        # |     |     |- Bit mask for mouse buttons
        # |     |     |  0x80: Not defined
        # |     |     |  0x40: Not defined
        # |     |     |  0x20: Not defined
        # |     |     |  0x10: Not defined
        # |     |     |  0x08: Forward mouse button
        # |     |     |  0x04: Middle mouse button
        # |     |     |  0x02: Right mouse button
        # |     |     |  0x01: Left mouse button
        # |     |     |     |- Mouse x position
        # |     |     |     |     |- Mouse y position
        # |     |     |     |     |     |- Vertical wheel position
        # |     |     |     |     |     |     |- Horizontal wheel position
        # 0xA1, 0x02, 0xXX, 0xXX, 0xXX, 0xXX, 0xXX]
        mouse_usb_telegram = [0xA1, 2, buttons_byte, x_pos_byte, y_pos_byte, v_wheel_byte, h_wheel_byte]
        self._bt_server.send(mouse_usb_telegram)

    @dbus_next.service.signal()
    def signal_host_change(self, client_names: 'as') -> 'as':
        return client_names

    @dbus_next.service.signal()
    def signal_clients_change(self, client_names: 'as') -> 'as':
        return client_names

    @dbus_next.service.signal()
    def signal_restart_info_hub(self) -> '':
        return

async def main():
    logging.basicConfig(format='BT %(levelname)s: %(message)s', level=logging.DEBUG)

    if not os.geteuid() == 0: # Check if user is root
        logging.error("Root permissions required: Execute as root or with sudo")
        return

    bt_server = BtServer()
    bt_server_task = asyncio.create_task( bt_server.run() )

    settings = Settings()
    settings.load_from_file()
    hotkey_config = HotkeyConfig(settings)
    hotkey_detector = HotkeyDetector(hotkey_config)
    kvm_dbus_service = KvmDbusService(settings, hotkey_detector, bt_server)
    kvm_dbus_service_task = asyncio.create_task( kvm_dbus_service.run() )

    main_future = asyncio.Future()

    def signal_handler(sig, frame):
        logging.error("System: Ctrl+C has been pressed - Shut down")
        main_future.set_result("")
    signal.signal(signal.SIGINT, signal_handler)

    await main_future # wait unitl signal interrupts

    kvm_dbus_service.stop()
    await kvm_dbus_service_task
    bt_server.stop()
    await bt_server_task
    logging.error("System: Shut down completed")

if __name__ == "__main__":
    asyncio.run( main() )

