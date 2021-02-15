#!/usr/bin/python3

import os
import json
import logging

class Settings(object):
    PATH_TO_FILE = "./conf/rpi-kvm-settings.json"

    def __init__(self):
        self._settings_dict = {
            "web": {
                "port": 8080
            },
            "hotkeys": {
                            # Bit Mask for control keys
                            # |- Right GUI
                            # |  |- Right ALT
                            # |  |  |- Right Shift
                            # |  |  |  |- Right Control
                            # |  |  |  |  |- Left GUI
                            # |  |  |  |  |  |- Left ALT
                            # |  |  |  |  |  |  |- Left Shift
                            # |  |  |  |  |  |  |  |- Left Control
                            # |  |  |  |  |  |  |  |   |- 6 pressed keys
                            #[0, 0, 0, 0, 0, 0, 0, 0], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
                "nextHost": [[0, 0, 0, 0, 0, 0, 0, 0], 0x47, 0x00, 0x00, 0x00, 0x00, 0x00] # KEY_SCROLLLOCK 71 -> 0x47
            }
        }

    def __getitem__(self, key):
        return self._settings_dict[key]

    def __str__(self):
        return json.dumps(self._settings_dict)

    def as_dict(self):
        return self._settings_dict

    def apply_settings_from_dict(self, data):
        errors = []
        changed = []
        for subject in self._settings_dict.keys():
            if subject in data:
                for element in self._settings_dict[subject].keys():
                    if element in data[subject]:
                        if data[subject][element] != self._settings_dict[subject][element]:
                            changed.append(f"Setting {subject}.{element} changed from {self._settings_dict[subject][element]} to {data[subject][element]}")
                            self._settings_dict[subject][element] = data[subject][element]
                    else:
                        errors.append(f"Element <{element}> not in received settings data subject <{subject}>")
            else:
                errors.append(f"Subject <{subject}> not in received settings data")
        for error in errors:
            logging.error(error)
        for change in changed:
            logging.info(change)
        if changed:
            self.save_to_file()
            return True
        else:
            return False

    def save_to_file(self):
        file_content = json.dumps(self._settings_dict, indent=4)
        with open(Settings.PATH_TO_FILE, 'w') as f:
            f.write(file_content)
        logging.info(f"Settings written to: {Settings.PATH_TO_FILE}")

    def load_from_file(self):
        if not os.path.exists(Settings.PATH_TO_FILE):
            logging.error(f"Settings file does not exist at: {Settings.PATH_TO_FILE}")
            logging.info(f"Create new settings file with init values at: {Settings.PATH_TO_FILE}")
            self.save_to_file()
            return
        with open(Settings.PATH_TO_FILE, 'r') as f:
            content = f.read()
            saved_settings_dict = json.loads(content)
            for subject in self._settings_dict.keys():
                if subject in saved_settings_dict:
                    for element in self._settings_dict[subject].keys():
                        if element in saved_settings_dict[subject]:
                            if saved_settings_dict[subject][element] != self._settings_dict[subject][element]:
                                self._settings_dict[subject][element] = saved_settings_dict[subject][element]


def main():
    logging.basicConfig(format='Settings %(levelname)s: %(message)s', level=logging.DEBUG)
    settings = Settings()
    settings.load_from_file()
    settings.save_to_file()
    print(settings)

if __name__ == "__main__":
    main()
