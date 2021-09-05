#!/usr/bin/python3

import os
import collections
import json
import logging

class PersistentClientOrder(object):
    PATH_TO_FILE = "./conf/rpi-kvm-client-order.json"

    def __init__(self):
        self._clients_order_dict = {
            "activeClient": "",
            "clients": {
                # "address": order,
                # "13:1A:7D:DA:71:11": 2,
                # "00:1A:7D:DA:71:11": 0,
                # "B3:1A:7D:DA:71:11": 1,
            }
        }

    def __getitem__(self, key):
        return self._clients_order_dict[key]

    def __str__(self):
        return json.dumps(self._clients_order_dict)

    def as_dict(self):
        return self._clients_order_dict

    @property
    def active_client(self):
        return self._clients_order_dict["activeClient"]

    @active_client.setter
    def active_client(self, new_value):
        self._clients_order_dict["activeClient"] = new_value
        self.save_to_file()

    @property
    def clients(self):
        return self._clients_order_dict["clients"]

    def apply_client_order_from_dict(self, data):
        for subject in self._clients_order_dict.keys():
            if subject in data:
                if isinstance(data[subject], dict):
                    self._clients_order_dict[subject].clear()
                    for element in data[subject].keys():
                        self._clients_order_dict[subject][element] = data[subject][element]
                else:
                    self._clients_order_dict[subject] = data[subject]
        self.save_to_file()
    
    def add_client(self, new_client):
        if new_client.address not in self.clients:
            self._clients_order_dict["clients"][new_client.address] = len(self._clients_order_dict["clients"])
            self.save_to_file()
    
    def sort_clients(self, client_addresses):
        sorted_clients_dict = dict()
        for client_address in client_addresses:
            if client_address in self.clients:
                sorted_clients_dict[self.clients[client_address]] = client_address
        return list(collections.OrderedDict(sorted(sorted_clients_dict.items())).values())

    def change_order_lower(self, client_address):
        if client_address in self.clients:
            cur_order = self.clients[client_address]
            if cur_order > 0:
                new_order = cur_order - 1
                list_of_orders = list(self.clients.values())
                if new_order in list_of_orders: 
                    index_of_client_at_new_order = list_of_orders.index(new_order)
                    client_address_at_new_order = list(self.clients.keys())[index_of_client_at_new_order]
                    self.clients[client_address_at_new_order] = cur_order
                self.clients[client_address] = new_order
                self.save_to_file()

    def change_order_higher(self, client_address):
        if client_address in self.clients:
            cur_order = self.clients[client_address]
            new_order = cur_order + 1
            list_of_orders = list(self.clients.values())
            if new_order in list_of_orders: 
                index_of_client_at_new_order = list_of_orders.index(new_order)
                client_address_at_new_order = list(self.clients.keys())[index_of_client_at_new_order]
                self.clients[client_address_at_new_order] = cur_order
            self.clients[client_address] = new_order
            self.save_to_file()

    def save_to_file(self):
        file_content = json.dumps(self._clients_order_dict, indent=4)
        with open(PersistentClientOrder.PATH_TO_FILE, 'w') as f:
            f.write(file_content)
        #logging.info(f"PersistentClientOrder written to: {PersistentClientOrder.PATH_TO_FILE}")

    def load_from_file(self):
        if not os.path.exists(PersistentClientOrder.PATH_TO_FILE):
            logging.error(f"PersistentClientOrder file does not exist at: {PersistentClientOrder.PATH_TO_FILE}")
            logging.info(f"Create new PersistentClientOrder file with init values at: {PersistentClientOrder.PATH_TO_FILE}")
            self.save_to_file()
            return
        with open(PersistentClientOrder.PATH_TO_FILE, 'r') as f:
            content = f.read()
            saved_clients_order_dict = json.loads(content)
            for subject in self._clients_order_dict.keys():
                if subject in saved_clients_order_dict:
                    if isinstance(saved_clients_order_dict[subject], dict):
                        for element in saved_clients_order_dict[subject].keys():
                            self._clients_order_dict[subject][element] = saved_clients_order_dict[subject][element]
                    else:
                        self._clients_order_dict[subject] = saved_clients_order_dict[subject]


def main():
    logging.basicConfig(format='PersistentClientOrder %(levelname)s: %(message)s', level=logging.DEBUG)
    client_order = PersistentClientOrder()
    client_order.load_from_file()
    client_order.save_to_file()
    print(client_order)

if __name__ == "__main__":
    main()
