#!/usr/bin/python3

import os
import asyncio
import dbus_next
from dbus_next.aio import MessageBus
from aiohttp import web
import json
import logging
from settings import Settings

class WebServer(object):
    def __init__(self, settings):
        self._settings = settings
        self._is_alive = False
        self._server_future = None
        self._app = web.Application()
        self._app.router.add_route('*', '/', self.root_handler)
        self._app.add_routes([web.get('/hello', self.hello)])
        self._app.add_routes([web.get('/clients', self.get_bt_clients)])
        self._app.add_routes([web.post('/connect_client', self.connect_client)])
        self._app.add_routes([web.post('/disconnect_client', self.disconnect_client)])
        self._app.add_routes([web.post('/switch_active_bt_host', self.switch_active_bt_host)])
        self._app.add_routes([web.get('/get_settings', self.get_settings)])
        self._app.add_routes([web.post('/set_settings', self.set_settings)])
        self._app.add_routes([web.post('/restart_service', self.restart_service)])
        self._app.router.add_static('/', "web/")

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

    async def _fetch_bt_clients(self):
        try:
            clients_info = await self._kvm_dbus_iface.call_get_clients_info()
            return clients_info
        except dbus_next.DBusError:
            logging.warning(f"D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()
            await self._fetch_bt_clients()

    async def _connect_bt_client(self, client_address):
        try:
            await self._kvm_dbus_iface.call_connect_client(client_address)
        except dbus_next.DBusError:
            logging.warning(f"D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()
            await self._connect_bt_client(client_address)

    async def _disconnect_bt_client(self, client_address):
        try:
            await self._kvm_dbus_iface.call_disconnect_client(client_address)
        except dbus_next.DBusError:
            logging.warning(f"D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()
            await self._disconnect_bt_client(client_address)

    async def _switch_active_bt_host(self, client_address):
        try:
            await self._kvm_dbus_iface.call_switch_active_host(client_address)
        except dbus_next.DBusError:
            logging.warning(f"D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()
            await self._disconnect_bt_client(client_address)

    async def run(self):
        logging.info(f"D-Bus service connecting...")
        await self._connect_to_dbus_service()

        self._is_alive = True
        while self._is_alive:
            self._server_future = asyncio.Future()
            logging.info("Starting web server")
            self._runner = web.AppRunner(self._app)
            await self._runner.setup()
            self._site = web.TCPSite(self._runner, None, self._settings["web"]["port"])
            await self._site.start()
            await self._server_future
            await self._site.stop()
    
    async def root_handler(self, request):
        return web.HTTPFound('/index.html')

    async def hello(self, request):
        return web.Response(text="Hello, world")

    async def get_bt_clients(self, request):
        clients_info = await self._fetch_bt_clients()
        return web.Response(text=clients_info)

    async def connect_client(self, request):
        data = await request.json()
        await self._connect_bt_client(data['clientAddress'])
        return web.Response()

    async def disconnect_client(self, request):
        data = await request.json()
        await self._disconnect_bt_client(data['clientAddress'])
        return web.Response()

    async def switch_active_bt_host(self, request):
        data = await request.json()
        await self._switch_active_bt_host(data['clientAddress'])
        return web.Response()

    async def get_settings(self, request):
        return web.Response(text=json.dumps({"settings": self._settings.as_dict()}))

    async def set_settings(self, request):
        data = await request.json()
        if "settings" in data:
            self._settings.apply_settings_from_dict(data["settings"])
        return web.Response()

    async def restart_service(self, request):
        data = await request.json()
        if "service" in data:
            if data["service"] == "web":
                logging.warning("Restart web service")
                self._server_future.set_result("")
            if data["service"] == "kvm":
                logging.warning("Restart KVM service")
                kvm_restart_cmd = "tmux new-session -d 'sudo /home/pi/rpi-kvm/rpi-kvm.sh restart'"
                os.system(kvm_restart_cmd)
            if data["service"] == "rpi":
                logging.warning("Restart Raspbarry Pi")
                os.system('sudo reboot -f')
        return web.Response()

async def main():
    logging.basicConfig(format='Web %(levelname)s: %(message)s', level=logging.DEBUG)
    settings = Settings()
    settings.load_from_file()
    server = WebServer(settings)
    await server.run()

if __name__ == "__main__":
    asyncio.run( main() )
