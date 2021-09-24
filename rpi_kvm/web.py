#!/usr/bin/python3

import os
import asyncio
import dbus_next
import socket
from dbus_next.aio import MessageBus
from aiohttp import web
import json
import logging
import common
from settings import Settings
from usb_hid_decoder import UsbHidDecoder
from clipboard import Clipboard

class WebServer(object):
    def __init__(self, settings):
        self._settings = settings
        self._server_url = ""
        self._is_alive = False
        self._server_future = None
        self._clipboard = Clipboard()
        self._clipboard.start()
        self._app = web.Application()
        self._app.router.add_route('*', '/', self.root_handler)
        self._app.add_routes([web.get('/hello', self.hello)])
        self._app.add_routes([web.get('/bt-clients-socket', self.bt_clients_websocket_handler)])
        self._app.add_routes([web.get('/clients', self.get_bt_clients)])
        self._app.add_routes([web.post('/connect_client', self.connect_client)])
        self._app.add_routes([web.post('/disconnect_client', self.disconnect_client)])
        self._app.add_routes([web.post('/remove_client', self.remove_client)])
        self._app.add_routes([web.post('/change_client_order', self.change_client_order)])
        self._app.add_routes([web.post('/switch_active_bt_host', self.switch_active_bt_host)])
        self._app.add_routes([web.get('/get_settings', self.get_settings)])
        self._app.add_routes([web.post('/set_settings', self.set_settings)])
        self._app.add_routes([web.post('/restart_service', self.restart_service)])
        self._app.add_routes([web.get('/get_keyboard_codes', self.get_keyboard_codes)])
        self._app.add_routes([web.get('/is_update_available', self.is_update_available)])
        self._app.add_routes([web.get('/perform_update', self.perform_update)])
        self._app.add_routes([web.get('/clipboard-socket', self._clipboard.websocket_handler)])
        self._app.add_routes([web.post('/clipboard-add', self._clipboard.add)])
        self._app.add_routes([web.post('/clipboard-clear-history', self._clipboard.clear_history)])
        self._app.add_routes([web.post('/clipboard-apply-entry', self._clipboard.apply_entry)])
        self._app.add_routes([web.post('/clipboard-clear-entry', self._clipboard.clear_entry)])
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

    async def _remove_bt_client(self, client_address):
        try:
            await self._kvm_dbus_iface.call_remove_client(client_address)
        except dbus_next.DBusError:
            logging.warning(f"D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()
            await self._remove_bt_client(client_address)

    async def _change_client_order(self, client_address, order_type):
        try:
            await self._kvm_dbus_iface.call_change_client_order(client_address, order_type)
        except dbus_next.DBusError:
            logging.warning(f"D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()
            await self._change_client_order(client_address, order_type)

    async def _switch_active_bt_host(self, client_address):
        try:
            await self._kvm_dbus_iface.call_switch_active_host(client_address)
        except dbus_next.DBusError:
            logging.warning(f"D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()
            await self._switch_active_bt_host(client_address)

    async def _trigger_reload_settings(self):
        try:
            await self._kvm_dbus_iface.call_reload_settings()
        except dbus_next.DBusError:
            logging.warning(f"D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()
            await self._trigger_reload_settings()

    async def _trigger_restart_info_hub(self):
        try:
            await self._kvm_dbus_iface.call_restart_info_hub()
        except dbus_next.DBusError:
            logging.warning(f"D-Bus connection terminated - reconnecting...")
            await self._connect_to_dbus_service()
            await self._trigger_restart_info_hub()

    async def run(self):
        logging.info(f"D-Bus service connecting...")
        await self._connect_to_dbus_service()

        self._is_alive = True
        while self._is_alive:
            self._server_future = asyncio.Future()
            self._server_url = f"http://{socket.gethostname()}:{self._settings['web']['port']}"
            logging.info(f"Starting web server on: {self._server_url}")
            self._runner = web.AppRunner(self._app)
            await self._runner.setup()
            self._site = web.TCPSite(self._runner, None, self._settings['web']['port'])
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

    async def bt_clients_websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        print("BT-Clients: Open websocket")
        while not ws.closed:
            await asyncio.sleep(1)
            clients_info = await self._fetch_bt_clients()
            await ws.send_json(clients_info)

        print('BT-Clients: websocket connection closed')
        return ws

    async def connect_client(self, request):
        data = await request.json()
        await self._connect_bt_client(data['clientAddress'])
        return web.Response()

    async def disconnect_client(self, request):
        data = await request.json()
        await self._disconnect_bt_client(data['clientAddress'])
        return web.Response()

    async def remove_client(self, request):
        data = await request.json()
        await self._remove_bt_client(data['clientAddress'])
        return web.Response()

    async def change_client_order(self, request):
        data = await request.json()
        await self._change_client_order(data['clientAddress'], data['order_type'])
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
            has_changed = self._settings.apply_settings_from_dict(data["settings"])
            if has_changed:
                await self._trigger_reload_settings()
        return web.Response()

    async def restart_service(self, request):
        data = await request.json()
        if "service" in data:
            if data["service"] == "info-hub":
                logging.warning("Restart info hub")
                await self._trigger_restart_info_hub()
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

    async def get_keyboard_codes(self, request):
        return web.Response(text=json.dumps({
            "keyboardCodes": {
                "keyCodes": UsbHidDecoder.KEY_CODES,
                "modifierKeys": UsbHidDecoder.MODIFIER_KEYS_BIT_MASK_VALUE
                }
            }))

    async def _is_git_update_available(self):
        _, stdout, _ = await common.System.exec_cmd("git rev-list HEAD...origin/main --count")
        return (stdout != b'0\n')

    async def is_update_available(self, request):
        is_updateable = await self._is_git_update_available()
        if not is_updateable:
            await common.System.exec_cmd("git fetch")
            is_updateable = await self._is_git_update_available()
        return web.Response(text=json.dumps({
            "isUpdateAvailable": is_updateable
            }))

    async def perform_update(self, request):
        await common.System.exec_cmd("git fetch")
        is_updateable = await self._is_git_update_available()
        is_update_successful = False
        has_update_performed = False
        if is_updateable:
            logging.info(f"Perfrom update via git merge")
            returncode, _, _ = await common.System.exec_cmd("git merge origin/main")
            is_update_successful = (returncode == 0)
            has_update_performed = True
        return web.Response(text=json.dumps({
            "isUpdateSuccessful": is_update_successful,
            "hasUpdatePerformed": has_update_performed
            }))


async def main():
    logging.basicConfig(format='Web %(levelname)s: %(message)s', level=logging.DEBUG)
    settings = Settings()
    settings.load_from_file()
    server = WebServer(settings)
    await server.run()

if __name__ == "__main__":
    asyncio.run( main() )
