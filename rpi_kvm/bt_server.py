#!/usr/bin/python3

import sys
import asyncio
import dbus_next
from dbus_next.aio import MessageBus
from dbus_next import Variant
import socket
import logging
import common
from bt_client import BtClient

class BtServer(object):
    NAME = "RPI-KVM"
    BT_HID_UUID = "00001124-0000-1000-8000-00805f9b34fb" # https://www.bluetooth.com/specifications/assigned-numbers/service-discovery/
    SDP_RECORD_PATH = sys.path[0] + "/../conf/sdp_record.xml" # file path of the sdp record to load

    BT_CONTROL_PORT = 17  # Service port - control port specified in the bluetooth HID specification
    BT_INTERRUPT_PORT = 19  # Service port - interrupt port specified in the bluetooth HID specification

    def __init__(self):
        self._loop = asyncio.get_event_loop()
        self._stop_event = False
        self._has_stopped = False
        self._clients = {}
        self._clients_connected = {}
        self._active_host = None
        self._handlers_on_clients_change = []

    def stop(self):
        self._stop_event = True

    async def run(self):
        await self._restart_and_init_bt()
        await self._register_bluez_profile()
        await self._connect_to_paired_clients()
        await self._listen_for_incomming_requests()
    
    def register_on_clients_change_handler(self, handler):
        self._handlers_on_clients_change.append(handler)

    def unregister_on_clients_change_handler(self, handler):
        if handler in self._handlers_on_clients_change:
            self._handlers_on_clients_change.remove(handler)

    async def _restart_and_init_bt(self):
        logging.info("Server: Configuring BT server name {}".format(BtServer.NAME))
        # start bluetooth server
        await common.System.exec_cmd(f"hciconfig hci0 down")
        await common.System.exec_cmd(f"hciconfig hci0 up")
        await common.System.exec_cmd(f"hciconfig hci0 class 0x0025C0")
        await common.System.exec_cmd(f"hciconfig hci0 name {BtServer.NAME}")
        # bluetooth server is discoverable
        await common.System.exec_cmd(f"hciconfig hci0 piscan")

    async def _register_bluez_profile(self):
        service_record = self._read_sdp_service_record()
        opts = {
            "AutoConnect": Variant('b', True),
            "ServiceRecord": Variant('s', service_record)
        }
        bus = await MessageBus(bus_type=dbus_next.BusType.SYSTEM).connect()
        # retrieve a proxy for the bluez profile interface
        introspection = await bus.introspect(
            "org.bluez", "/org/bluez")
        manager_obj = bus.get_proxy_object(
            "org.bluez", "/org/bluez", introspection)
        manager_itf = manager_obj.get_interface("org.bluez.ProfileManager1")
        await manager_itf.call_register_profile("/org/bluez/hci0", BtServer.BT_HID_UUID, opts)

    def _read_sdp_service_record(self):
        content = ""
        with open(BtServer.SDP_RECORD_PATH, 'r') as f:
            content = f.read()
        return content

    async def _connect_to_paired_clients(self):
        logging.info("Server: Connect to already paired clients")
        bus = await MessageBus(bus_type=dbus_next.BusType.SYSTEM).connect()
        # retrieve a proxy for the bluez profile interface
        introspection = await bus.introspect(
            "org.bluez", "/")
        dbus_object_manager_obj = bus.get_proxy_object(
            "org.bluez", "/", introspection)
        dbus_object_manager_itf = dbus_object_manager_obj.get_interface("org.freedesktop.DBus.ObjectManager")
        managed_objects = await dbus_object_manager_itf.call_get_managed_objects()

        for obj_path in list(managed_objects):
            if  "org.bluez.Device1" in managed_objects[obj_path]:
                asyncio.create_task( self._connect_to_client(obj_path) )

    async def _connect_to_client(self, device_object_path):
        client = await BtClient.create_via_device_object_path(device_object_path)
        if client.address in self._clients:
            logging.info(f"Server: Client {client.name} already connected. Skipping.")
            return
        client.connect()
        self._add_client(client)

    async def _listen_for_incomming_requests(self):
        logging.info("Server: Waiting for incomming connections")
        self.control_socket = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
        self.interrupt_socket = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
        self.control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.interrupt_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.control_socket.setblocking(False)
        self.interrupt_socket.setblocking(False)
        # bind these sockets to a port - port zero to select next available
        self.control_socket.bind((socket.BDADDR_ANY, self.BT_CONTROL_PORT))
        self.interrupt_socket.bind((socket.BDADDR_ANY, self.BT_INTERRUPT_PORT))

        # Start listening on the server sockets
        self.control_socket.listen(5)
        self.interrupt_socket.listen(5)

        while not self._stop_event:
            try:
                self._check_for_client_communication_change()
                client_control_socket, (client_address, client_port) = await asyncio.wait_for(
                    self._loop.sock_accept(self.control_socket), timeout=2)
                client_interrupt_socket, (client_address, client_port) = await asyncio.wait_for(
                    self._loop.sock_accept(self.interrupt_socket), timeout=2)
                if client_address in self._clients:
                    client = self._clients[client_address]
                else:
                    client = await BtClient.create_via_address(client_address)
                    self._add_client(client)
                client.accept_connection(client_control_socket, client_interrupt_socket)
            except asyncio.TimeoutError:
                await asyncio.sleep(3)

        logging.warning("Server: Closing receiving server sockets")
        self.control_socket.close()
        self.interrupt_socket.close()

        logging.warning("Server: Trigger stop on all clients")
        for client_address, client in self._clients.items():
            client.stop()
        logging.warning("Server: Stop on all clients triggered - Wait till done")
        for client_address, client in self._clients.items():
            await client.join()
        logging.warning("Server: All clients stopped")
        logging.warning("Server: Stopped successfully")

    def _add_client(self, client):
        if client.address in self._clients:
            logging.info(f"Server: Client {client.name} was connected before - Stop old instance")
            self._clients[client.address].stop()
        self._clients[client.address] = client
        if not self._active_host:
            logging.info(f"Server: Active host: {client.name}")
            self._active_host = client
        elif self._active_host.address == client.address:
            logging.info(f"Server: Reconnection of active host: {client.name}")
            self._active_host = client
        self._notify_on_clients_change()

    def _check_for_client_communication_change(self):
        old_clients_connected = self._clients_connected.copy()
        self._clients_connected = {}
        for client_address, client in self._clients.items():
            if client.is_alive:
                self._clients_connected[client_address] = client
        if self._clients_connected != old_clients_connected:
            self._notify_on_clients_change()

    def switch_to_next_connected_host(self):
        if len(self._clients_connected) > 1:
            next_host = self._get_connected_client_addresses()[1]
            self._active_host = self._clients_connected[next_host]
        elif len(self._clients_connected) == 1:
            next_host = self._get_connected_client_addresses()[0]
            self._active_host = self._clients_connected[next_host]

    def switch_active_host_to(self, client_address):
        if client_address in self._clients:
            self._active_host = self._clients[client_address]

    def _get_connected_client_addresses(self):
        if self._active_host and len(self._clients_connected) > 0:
            client_addresses = list(self._clients_connected.keys())
            if self._active_host.address in client_addresses:
                cur_active_index = client_addresses.index(self._active_host.address)
            else:
                cur_active_index = 0
            client_addresses = [*client_addresses[cur_active_index:], *client_addresses[:cur_active_index]]
            return client_addresses
        else:
            return None

    def _notify_on_clients_change(self):
        for handler in self._handlers_on_clients_change:
            handler.on_clients_change(self.get_connected_client_names())

    def get_connected_client_names(self):
        client_names = []
        if self._active_host:
            client_addresses = self._get_connected_client_addresses()
            if client_addresses:
                client_names = [self._clients[client_address].name for client_address in client_addresses]
                if not self._active_host.address in client_addresses:
                    client_names.insert(0, f"off: {self._active_host.name}")
            else:
                client_names.insert(0, f"off: {self._active_host.name}")
        else:
            client_names = [""]
        return client_names

    def get_clients_info_dict(self):
        infos = []
        for client_address, client in self._clients.items():
            info_dict = client.info
            info_dict["isHost"] = (self._active_host.address == client.address)
            infos.append(info_dict)
        return {"clients": infos}

    def connect_client(self, client_address):
        if client_address in self._clients:
            client = self._clients[client_address]
            logging.info(f"Server: External trigger: Connect {client.name} ({client.address})")
            client.connect()

    def disconnect_client(self, client_address):
        if client_address in self._clients:
            client = self._clients[client_address]
            logging.info(f"Server: External trigger: Disconnect {client.name} ({client.address})")
            client.stop()

    def send(self, message):
        if self._active_host:
            self._active_host.send(message)

