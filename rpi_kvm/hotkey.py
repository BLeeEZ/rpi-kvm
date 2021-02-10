import enum
import numpy
from usb_hid_decoder import UsbHidDecoder

class HotkeyAktion(enum.Enum):
    SwitchToNextHost = 1
    IndicateHost = 2

# Bit Mask for control keys
# |- Right GUI - Windows Key
# |  |- Right ALT
# |  |  |- Right Shift
# |  |  |  |- Right Control
# |  |  |  |  |- Left GUI
# |  |  |  |  |  |- Left ALT
# |  |  |  |  |  |  |- Left Shift
# |  |  |  |  |  |  |  |- Left Control
# |  |  |  |  |  |  |  |   |- 6 pressed keys
#[0, 0, 0, 0, 0, 0, 0, 0], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
class HotkeyConfig(object):
    def __init__(self):
        self.keys = {
            HotkeyAktion.SwitchToNextHost:
                [
                    [[0, 0, 0, 0, 0, 0, 0, 0], 71, 0x00, 0x00, 0x00, 0x00, 0x00] # KEY_SCROLLLOCK 71
                ],
            HotkeyAktion.IndicateHost:
                [
                    [[0, 0, 0, 0, 0, 0, 0, 0], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    [[0, 0, 0, 0, 0, 0, 0, 0], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    [[0, 0, 0, 0, 0, 0, 0, 0], 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                ],
        }
        self.__reduce_keys_to_compareable_format()

    def __reduce_keys_to_compareable_format(self):
        for action, hotkey_combination in self.keys.items():
            hotkey_combination.reverse()
            for index, keyboard_input in enumerate(hotkey_combination):
                hotkey_combination[index] = self.__combine_bitmask_and_remove_vendor_reserved(keyboard_input)
    
    def __combine_bitmask_and_remove_vendor_reserved(self, keyboard_input):
        modifiers_int = UsbHidDecoder.convert_modifier_bit_mask_to_int(keyboard_input[0])
        return [modifiers_int, *keyboard_input[1:7]]

class RingBuffer(object):
    def __init__(self, size):
        self.size = size
        self.reset()

    def reset(self):
        self.data = [None for i in range(self.size)]

    def append(self, x):
        self.data.insert(0, x)
        self.data.pop(self.size)

    def get(self):
        return self.data

class HotkeyDetector(object):
    def __init__(self, hotKeyConfig):
        self._config = hotKeyConfig
        self._hot_keys = self._config.keys
        self._key_strokes = RingBuffer(3)
        self.activation = None

    def evaluate_new_input(self, new_input):
        self._key_strokes.append(new_input)
        self.activation = None
        for action, key_combination in self._hot_keys.items():
            if numpy.array_equal(key_combination, self._key_strokes.get()[:len(key_combination)]):
                self.activation = action
                self._key_strokes.reset()
                break
        return self.activation

if __name__ == "__main__":
    config = HotkeyConfig()
    detector = HotkeyDetector(config)
    print(detector.evaluate_new_input([0, 0, 0, 0, 0, 0, 0]) == None)
    print(detector.evaluate_new_input([0, 0x47, 0, 0, 0, 0, 0]) == None)
    print(detector.evaluate_new_input([0, 0, 0, 0, 0, 0, 0]) == None)
    print(detector.evaluate_new_input([0, 0x47, 0, 0, 0, 0, 0]) == HotkeyAktion.SwitchToNextHost)
    print(detector.evaluate_new_input([0, 0, 0, 0, 0, 0, 0]) == None)
