import asyncio
import dbus_next
from dbus_next.aio import MessageBus
import socket
import enum
import logging
import common

class BtConnectionRole(enum.Enum):
    Master = 1
    Slave = 2
    NotConnected = 3

class BtClient(object):
    BT_CONTROL_PORT = 17  # Service port - control port specified in the bluetooth HID specification
    BT_INTERRUPT_PORT = 19  # Service port - interrupt port specified in the bluetooth HID specification

    @staticmethod
    async def create_via_address(address):
        client = BtClient(address)
        await client._connect_to_dbus_service()
        return client

    @staticmethod
    async def create_via_device_object_path(device_object_path):
        address = BtClient.get_mac_address_from_devie_object_path(device_object_path)
        client = BtClient(address)
        await client._connect_to_dbus_service()
        return client

    @staticmethod
    def get_mac_address_from_devie_object_path(device_object_path):
        return device_object_path[-17:].replace("_",":")

    @staticmethod
    def get_device_object_path_from_mac_address(device_object_path):
        return "/org/bluez/hci0/dev_" + device_object_path.replace(":","_")

    def __init__(self, address):
        self._address = address
        self._device_object_path = BtClient.get_device_object_path_from_mac_address(self._address)
        self._is_alive = True
        self._stop_event = False
        self._is_connected = False
        self._is_bluez_connected = True
        self._control_socket = None
        self._interrupt_socket = None
        self._loop = asyncio.get_event_loop()
        self._message_queue = asyncio.Queue()
        self._task = None
        self._bt_master_task = None
        self._bt_check_alive_task = None

    @property
    def address(self):
        return self._address

    @property
    def object_path(self):
        return self._device_object_path

    @property
    def name(self):
        return self._name

    @property
    def is_alive(self):
        if self._task:
            return not self._task.done()
        else:
            return False

    @property
    def is_connected(self):
        return self._is_connected

    @property
    def info(self):
        info_dict = {}
        info_dict["name"] = self.name
        info_dict["address"] = self.address
        info_dict["isConnected"] = self.is_connected
        return info_dict

    def connect(self):
        if not self._task or self._task.done():
            self._stop_event = False
            self._task = asyncio.create_task(self._run())

    def accept_connection(self, control_socket, interrupt_socket):
        if not self._task or self._task.done():
            self._control_socket = control_socket
            self._interrupt_socket = interrupt_socket
            self._stop_event = False
            self._task = asyncio.create_task(self._run())

    async def _establish_socket_connection(self):
        if self._control_socket and self._interrupt_socket:
            logging.debug(f"{self.name}: Incoming socket connection from {self.name} ({self.address})")
            self._handle_state_at_successfull_connection()
        else:
            logging.debug(f"{self.name}: Establish socket connection to {self.name} ({self.address})")
            try:
                self._control_socket = socket.socket(
                    socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
                await self._loop.run_in_executor(None, lambda: self._control_socket.connect((self.address, self.BT_CONTROL_PORT)))
                self._control_socket.setblocking(False)
                self._interrupt_socket = socket.socket(
                    socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
                await self._loop.run_in_executor(None, lambda: self._interrupt_socket.connect((self.address, self.BT_INTERRUPT_PORT)))
                self._interrupt_socket.setblocking(False)
                self._handle_state_at_successfull_connection()
            except Exception as e:
                logging.error(f"{self.name}: Exception during connect: {e}")
                self._disconnect()
        if self._is_connected:
            self._enshure_bt_master()
            self._checking_connection_state_periodically()

    def _handle_state_at_successfull_connection(self):
        self._message_queue = asyncio.Queue()
        self._is_connected = True

    def _disconnect(self):
        if self._control_socket:
            self._control_socket.close()
            self._control_socket = None
        if self._interrupt_socket:
            self._interrupt_socket.close()
            self._interrupt_socket = None
        self._is_connected = False

    def stop(self):
        self._stop_event = True

    async def join(self):
        await self._task

    async def _connect_to_dbus_service(self):
        self._bluez_obj = None
        while not self._bluez_obj:
            try:
                self._dbus = await MessageBus(bus_type=dbus_next.BusType.SYSTEM).connect()
                introspection = await self._dbus.introspect(
                    "org.bluez", self._device_object_path)
                self._bluez_obj = self._dbus.get_proxy_object(
                    "org.bluez", self._device_object_path, introspection)
                self._bluez_itf = self._bluez_obj.get_interface("org.bluez.Device1")
                self._bluez_props = self._bluez_obj.get_interface("org.freedesktop.DBus.Properties")
                logging.debug(f"{self._address}: D-Bus bluez object connected")
                self._name = await self._bluez_itf.get_name()
                logging.debug(f"{self._address}: Name resolves to {self._name}")
                self._bluez_props.on_properties_changed(self._on_properties_changed)
            except dbus_next.DBusError:
                logging.warning(f"{self._address}: D-Bus bluez object available - reconnecting...")
                await asyncio.sleep(5)

    def _on_properties_changed(self, interface_name, changed_properties, invalidated_properties):
        for changed, variant in changed_properties.items():
            logging.debug(f'{self._name}: D-Bus bluez property changed: {changed} - {variant.value}')
            if changed == "Connected":
                self._is_bluez_connected = variant.value

    async def _run(self):
        if self._stop_event: return
        await self._establish_socket_connection()
        if self._is_connected:
            logging.info(f"\033[0;32m{self.name}: Connection established ({self.address})\033[0m")
        while self._is_connected and not self._stop_event:
            message = ""
            try:
                message = await asyncio.wait_for(self._message_queue.get(), timeout=2)
                await self._loop.sock_sendall(self._interrupt_socket, bytes(message))
                self._message_queue.task_done()
            except asyncio.QueueEmpty:
                pass
            except asyncio.TimeoutError:
                pass
            except socket.error:
                logging.error(f"{self._name}: Socket error during send")
                self._disconnect()
            except:
                logging.error(f"{self._name}: Message could not be sed: {message}")
                raise

        logging.info(f"\033[0;31m{self.name}: Connection terminated - client closed ({self.address})\033[0m")
        self._disconnect()

    def _enshure_bt_master(self):
        if not self._bt_master_task or self._bt_master_task.done():
            self._bt_master_task = asyncio.create_task(self._switch_to_master())

    async def _switch_to_master(self):
        logging.info(f"{self._name}: Enshure connection role {BtConnectionRole.Master.name}")
        connection_role = await self._get_connection_role()
        while (connection_role == BtConnectionRole.Slave) and not self._stop_event:
            try:
                await common.System.exec_cmd(f"hcitool sr {self._address} MASTER")
            except Exception as exc:
                logging.debug(f"{self._name}: Connection role switch exception: {exc}")
            await asyncio.sleep(2)
            connection_role = await self._get_connection_role()
        logging.info(f"{self._name}: Connection role is {connection_role.name}")

    def _checking_connection_state_periodically(self):
        if not self._bt_check_alive_task or self._bt_check_alive_task.done():
            self._bt_check_alive_task = asyncio.create_task(self._send_periodic_alive_messages())

    async def _send_periodic_alive_messages(self):
        logging.debug(f"{self._name}: Sending periodic messages to check connection state started")
        while self._is_connected and not self._stop_event:
            await asyncio.sleep(4)
            # sending an empty message to check if socket connection is still alive
            self.send(bytes([0, 0, 0, 0]))
        logging.debug(f"{self._name}: Sending periodic messages to check connection state stopped")

    async def _get_connection_role(self):
        returncode, stdout, stderr = await common.System.exec_cmd("hcitool con")
        for line in stdout.decode("utf-8").splitlines():
            if line.find(self._address) >= 0:
                if line.find("SLAVE") >= 0:
                    return BtConnectionRole.Slave
                if line.find("MASTER") >= 0:
                    return BtConnectionRole.Master
        return BtConnectionRole.NotConnected

    def send(self, message):
        if self._is_connected:
            self._message_queue.put_nowait(message)
