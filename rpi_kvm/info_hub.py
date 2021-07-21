#!/usr/bin/python3

import asyncio
import dbus_next
from dbus_next.aio import MessageBus
from lcd import LcdDisplay, LcdLineStyle
import time
import logging

class InfoHub(object):
    def __init__(self):
        self._display = LcdDisplay()
        self._current_host = ""
        self._next_host = None
        self._np1_host = None
        self._prev_host = None
        self._is_restart_triggered = False

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
                logging.info("D-Bus service connected")
            except dbus_next.DBusError:
                logging.warning("D-Bus service not available - reconnecting...")
                await asyncio.sleep(5)

    async def _register_to_dbus_signals(self):
        logging.info("Register on D-Bus signals")
        try:
            self._kvm_dbus_iface.on_signal_host_change(self._handle_clients_change)
            self._kvm_dbus_iface.on_signal_clients_change(self._handle_clients_change)
            self._kvm_dbus_iface.on_signal_restart_info_hub(self._handle_restart_info_hub)
        except dbus_next.DBusError:
            logging.warning("D-Bus service not available - reconnecting...")
            await self._connect_to_dbus_service()
            await self._register_to_dbus_signals()

    def _handle_restart_info_hub(self):
        logging.info("Restart received")
        self._is_restart_triggered = True

    async def _perform_restart(self):
        self._is_restart_triggered = False
        self._display.stop()
        self._display.set_backlight(True)
        await asyncio.sleep(0.5)
        self._display.cleanup()
        hub_task = asyncio.create_task(self.run(is_restart=True))
        await hub_task

    async def _fetch_and_display_clients(self):
        try:
            clients = await self._kvm_dbus_iface.call_get_connected_client_names()
            self._handle_clients_change(clients)
        except dbus_next.DBusError:
            logging.warning(f"{self._idev.path}: D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()
            await self._fetch_and_display_clients()

    def _handle_clients_change(self, clients):
        if self._current_host != clients[0]:
            logging.info(f"New host: {clients[0]}")
        else:
            logging.info(f"Clients changed")
        self._current_host = clients[0]
        self._next_host = clients[1] if len(clients) > 1 else None
        self._np1_host = clients[2] if len(clients) > 2 else None
        self._prev_host = clients[-1]
        self._display_clients_info()

    def _display_clients_info(self):
        self._display.send_string(self._current_host, LcdDisplay.LCD_LINE_1, LcdLineStyle.Centred)
        next_host_string = ""
        if self._next_host:
            next_host_string = f"{self._next_host}"
            next_host_string.ljust(LcdDisplay.LCD_WIDTH," ")
            next_host_string = next_host_string[:LcdDisplay.LCD_WIDTH-2] + ">>"
        self._display.send_string(next_host_string, LcdDisplay.LCD_LINE_3, LcdLineStyle.RightJustified)
        np1_host_string = ""
        if self._np1_host:
            np1_host_string = f"{self._np1_host}"
            np1_host_string.ljust(LcdDisplay.LCD_WIDTH," ")
            np1_host_string = np1_host_string[:LcdDisplay.LCD_WIDTH-2] + " >"
        self._display.send_string(np1_host_string, LcdDisplay.LCD_LINE_4, LcdLineStyle.RightJustified)
        #self._display.send_string("< " + self._prev_host, LcdDisplay.LCD_LINE_4, LcdLineStyle.LeftJustified)

    def cleanup(self):
        self._display.cleanup()

    async def _show_welcome(self):
        logging.info("Indicate start via backlight flash")
        self._display.set_backlight(True)
        await asyncio.sleep(0.5)
        self._display.set_backlight(False)
        await asyncio.sleep(0.5)
        self._display.set_backlight(True)
        await asyncio.sleep(0.5)

        self._display.send_string("--------------------", LcdDisplay.LCD_LINE_1, LcdLineStyle.Centred)
        self._display.send_string("Rasbperry Pi", LcdDisplay.LCD_LINE_2, LcdLineStyle.Centred)
        self._display.send_string("K(V)M", LcdDisplay.LCD_LINE_3, LcdLineStyle.Centred)
        self._display.send_string("--------------------", LcdDisplay.LCD_LINE_4, LcdLineStyle.Centred)
        await asyncio.sleep(2)
        self._display.blank()
    
    async def run(self, is_restart = False):
        logging.info(f"Starting display")
        asyncio.create_task(self._display.run())
        await asyncio.sleep(0.5)
        await self._show_welcome()

        if not is_restart:
            logging.info(f"D-Bus service connecting...")
            await self._connect_to_dbus_service()
            await self._register_to_dbus_signals() # ready to handle signals and to display them
        await self._fetch_and_display_clients()

        logging.info(f"Starting date/time loop")
        while True:
            if self._is_restart_triggered:
                await self._perform_restart()
            lt = time.localtime(time.time())
            time_str = f"{lt.tm_mday:02}.{lt.tm_mon:02}.{lt.tm_year}     {lt.tm_hour:02}:{lt.tm_min:02}"
            self._display.send_string(time_str, LcdDisplay.LCD_LINE_2, LcdLineStyle.Centred)
            await asyncio.sleep(5)

async def main():
    logging.basicConfig(format='Hub %(levelname)s: %(message)s', level=logging.INFO)
    hub = InfoHub()
    try:
        hub_task = asyncio.create_task(hub.run())
        await hub_task
    except KeyboardInterrupt:
        raise
    finally:
        hub.cleanup()
 
if __name__ == '__main__':
    asyncio.run( main() )
