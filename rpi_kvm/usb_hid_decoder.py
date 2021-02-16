import logging

class UsbHidDecoder(object):
    # Python translation of the USB - HID Usage Tables:
    # https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf
    # in version 1.12
    # The dict translates table 12 - Keyboard/Keypad Page
    # The table can be found on page 53
    KEY_CODES = {
        "KEY_RESERVED": 0,
        "KEY_ERR_OVF": 1, # Keyboard ErrorRollOver - Too many keys are pressed
        # Keyboard POSTFail: 2
        # Keyboard ErrorUndefined: 3
        "KEY_A": 4,
        "KEY_B": 5,
        "KEY_C": 6,
        "KEY_D": 7,
        "KEY_E": 8,
        "KEY_F": 9,
        "KEY_G": 10,
        "KEY_H": 11,
        "KEY_I": 12,
        "KEY_J": 13,
        "KEY_K": 14,
        "KEY_L": 15,
        "KEY_M": 16,
        "KEY_N": 17,
        "KEY_O": 18,
        "KEY_P": 19,
        "KEY_Q": 20,
        "KEY_R": 21,
        "KEY_S": 22,
        "KEY_T": 23,
        "KEY_U": 24,
        "KEY_V": 25,
        "KEY_W": 26,
        "KEY_X": 27,
        "KEY_Y": 28,
        "KEY_Z": 29,
        "KEY_1": 30,
        "KEY_2": 31,
        "KEY_3": 32,
        "KEY_4": 33,
        "KEY_5": 34,
        "KEY_6": 35,
        "KEY_7": 36,
        "KEY_8": 37,
        "KEY_9": 38,
        "KEY_0": 39,
        "KEY_ENTER": 40,
        "KEY_ESC": 41,
        "KEY_BACKSPACE": 42,
        "KEY_TAB": 43,
        "KEY_SPACE": 44,
        "KEY_MINUS": 45,
        "KEY_EQUAL": 46,
        "KEY_LEFTBRACE": 47,
        "KEY_RIGHTBRACE": 48,
        "KEY_BACKSLASH": 49,
        "KEY_HASHTILDE": 50,
        "KEY_SEMICOLON": 51,
        "KEY_APOSTROPHE": 52,
        "KEY_GRAVE": 53,
        "KEY_COMMA": 54,
        "KEY_DOT": 55,
        "KEY_SLASH": 56,
        "KEY_CAPSLOCK": 57,
        "KEY_F1": 58,
        "KEY_F2": 59,
        "KEY_F3": 60,
        "KEY_F4": 61,
        "KEY_F5": 62,
        "KEY_F6": 63,
        "KEY_F7": 64,
        "KEY_F8": 65,
        "KEY_F9": 66,
        "KEY_F10": 67,
        "KEY_F11": 68,
        "KEY_F12": 69,
        "KEY_SYSRQ": 70,
        "KEY_SCROLLLOCK": 71,
        "KEY_PAUSE": 72,
        "KEY_INSERT": 73,
        "KEY_HOME": 74,
        "KEY_PAGEUP": 75,
        "KEY_DELETE": 76,
        "KEY_END": 77,
        "KEY_PAGEDOWN": 78,
        "KEY_RIGHT": 79,
        "KEY_LEFT": 80,
        "KEY_DOWN": 81,
        "KEY_UP": 82,
        "KEY_NUMLOCK": 83,
        "KEY_KPSLASH": 84,
        "KEY_KPASTERISK": 85,
        "KEY_KPMINUS": 86,
        "KEY_KPPLUS": 87,
        "KEY_KPENTER": 88,
        "KEY_KP1": 89,
        "KEY_KP2": 90,
        "KEY_KP3": 91,
        "KEY_KP4": 92,
        "KEY_KP5": 93,
        "KEY_KP6": 94,
        "KEY_KP7": 95,
        "KEY_KP8": 96,
        "KEY_KP9": 97,
        "KEY_KP0": 98,
        "KEY_KPDOT": 99,
        "KEY_102ND": 100,
        "KEY_COMPOSE": 101,
        "KEY_POWER": 102,
        "KEY_KPEQUAL": 103,
        "KEY_F13": 104,
        "KEY_F14": 105,
        "KEY_F15": 106,
        "KEY_F16": 107,
        "KEY_F17": 108,
        "KEY_F18": 109,
        "KEY_F19": 110,
        "KEY_F20": 111,
        "KEY_F21": 112,
        "KEY_F22": 113,
        "KEY_F23": 114,
        "KEY_F24": 115,
        "KEY_OPEN": 116,
        "KEY_HELP": 117,
        "KEY_PROPS": 118,
        "KEY_FRONT": 119,
        "KEY_STOP": 120,
        "KEY_AGAIN": 121,
        "KEY_UNDO": 122,
        "KEY_CUT": 123,
        "KEY_COPY": 124,
        "KEY_PASTE": 125,
        "KEY_FIND": 126,
        "KEY_MUTE": 127,
        "KEY_VOLUMEUP": 128,
        "KEY_VOLUMEDOWN": 129,
        # Keyboard Locking Caps Lock: 130
        # Keyboard Locking Num Lock: 131
        # Keyboard Locking Scroll Lock: 132
        "KEY_KPCOMMA": 133,
        # Keypad Equal Sign: 134
        "KEY_RO": 135,
        "KEY_KATAKANAHIRAGANA": 136,
        "KEY_YEN": 137,
        "KEY_HENKAN": 138,
        "KEY_MUHENKAN": 139,
        "KEY_KPJPCOMMA": 140,
        # Keyboard International7: 141
        # Keyboard International8: 142
        # Keyboard International9: 143
        "KEY_HANGEUL": 144,
        "KEY_HANJA": 145,
        "KEY_KATAKANA": 146,
        "KEY_HIRAGANA": 147,
        "KEY_ZENKAKUHANKAKU": 148,

        "KEY_KPLEFTPAREN": 182, # Keypad (
        "KEY_KPRIGHTPAREN": 183, # Keypad )

        "KEY_LEFTCTRL": 224,
        "KEY_LEFTSHIFT": 225,
        "KEY_LEFTALT": 226,
        "KEY_LEFTMETA": 227,
        "KEY_RIGHTCTRL": 228,
        "KEY_RIGHTSHIFT": 229,
        "KEY_RIGHTALT": 230,
        "KEY_RIGHTMETA": 231,
        "KEY_PLAYPAUSE": 232,
        "KEY_STOPCD": 233,
        "KEY_PREVIOUSSONG": 234,
        "KEY_NEXTSONG": 235,
        "KEY_EJECTCD": 236,
        "KEY_WWW": 240,
        "KEY_BACK": 241,
        "KEY_FORWARD": 242,
        "KEY_MEDIA_STOP": 243,
        "KEY_MEDIA_FIND": 244,
        "KEY_SCROLLUP": 245,
        "KEY_SCROLLDOWN": 246,
        "KEY_EDIT": 247,
        "KEY_SLEEP": 248,
        "KEY_COFFEE": 249,
        "KEY_REFRESH": 250,
        "KEY_CALC": 251
    }

    MODIFIER_KEYS_BIT_MASK_INDEX = {
        "KEY_RIGHTMETA": 0,
        "KEY_RIGHTALT": 1,
        "KEY_RIGHTSHIFT": 2,
        "KEY_RIGHTCTRL": 3,
        "KEY_LEFTMETA": 4,
        "KEY_LEFTALT": 5,
        "KEY_LEFTSHIFT": 6,
        "KEY_LEFTCTRL": 7
    }

    MODIFIER_KEYS_BIT_MASK_VALUE = {
        "KEY_RIGHTMETA": 0x80,
        "KEY_RIGHTALT": 0x40,
        "KEY_RIGHTSHIFT": 0x20,
        "KEY_RIGHTCTRL": 0x10,
        "KEY_LEFTMETA": 0x08,
        "KEY_LEFTALT": 0x04,
        "KEY_LEFTSHIFT": 0x02,
        "KEY_LEFTCTRL": 0x01
    }

    BIT_MASK = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]

    @staticmethod
    def is_modifier_key(evdev_keycode):
        if type(evdev_keycode) == list:
            return False
        else:
            return (evdev_keycode in UsbHidDecoder.MODIFIER_KEYS_BIT_MASK_INDEX)

    @staticmethod
    def convert_modifier_bit_mask_to_int(modifier_bit_mask):
        modifier_int = 0
        for i in range(0, 8):
            if modifier_bit_mask[i]: modifier_int += UsbHidDecoder.BIT_MASK[i]
        return modifier_int

    @staticmethod
    def encode_regular_key(evdev_keycode):
        if type(evdev_keycode) == list:
            for keycode in evdev_keycode:
                if keycode in UsbHidDecoder.KEY_CODES:
                    return UsbHidDecoder.KEY_CODES[keycode]
            logging.error(f"USB-HID: Keycode '{evdev_keycode}' could not be mapped to an usb integer value")
            return 0
        else:
            if evdev_keycode in UsbHidDecoder.KEY_CODES:
                return UsbHidDecoder.KEY_CODES[evdev_keycode]
            else:
                logging.error(f"USB-HID: Keycode '{evdev_keycode}' could not be mapped to an usb integer value")
                return 0

    @staticmethod
    def encode_modifier_key_index(evdev_keycode):
        return UsbHidDecoder.MODIFIER_KEYS_BIT_MASK_INDEX[evdev_keycode]

    @staticmethod
    def encode_mouse_button_index(evdev_event_code):
        if evdev_event_code >= 272 and evdev_event_code <= 276:
            return 279 - evdev_event_code
        else:
            return -1

    @staticmethod
    def enshure_byte_size(integer):
        return min(127, max(-128, integer)) & 255