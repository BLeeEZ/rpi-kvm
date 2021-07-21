#!/usr/bin/python3

import RPi.GPIO as GPIO
import asyncio
import enum
import time
import logging
 
# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
LED_ON = 15
 
# Define some device constants
LCD_CHR = True
LCD_CMD = False
 
class LcdLineStyle(enum.Enum):
    LeftJustified = 1
    Centred = 2
    RightJustified = 3

class LcdCmd(enum.Enum):
    SendString = 1
    Blank = 2
    BacklightSet = 3

class LcdDisplay(object):
    LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
    LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
    LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005
    # Maximum characters per line
    LCD_WIDTH = 20
 
    def __init__(self):
        self._queue = asyncio.Queue()

    def send_string(self, message, line, style):
        # Send string to display
        # style=1 Left justified
        # style=2 Centred
        # style=3 Right justified
        
        if style == LcdLineStyle.LeftJustified:
            message = message.ljust(LcdDisplay.LCD_WIDTH," ")
        elif style == LcdLineStyle.Centred:
            message = message.center(LcdDisplay.LCD_WIDTH," ")
        elif style == LcdLineStyle.RightJustified:
            message = message.rjust(LcdDisplay.LCD_WIDTH," ")
        self._queue.put_nowait((LcdCmd.SendString, message, line))

    def blank(self):
        self._queue.put_nowait((LcdCmd.Blank, None, None))

    def cleanup(self):
        logging.warning("Cleanup start")
        GPIO.cleanup()
        logging.warning("Cleanup done")
        
    def set_backlight(self, flag):
        self._queue.put_nowait((LcdCmd.BacklightSet, flag, None))

    async def run(self):
        await self._init()
        self._is_task_active = True
        while self._is_task_active:
            (cmd, arg1, arg2) = await self._queue.get()
            if LcdCmd.SendString == cmd:
                await self._change_active_line(arg2)
                for i in range(LcdDisplay.LCD_WIDTH):
                    await self._send_byte(ord(arg1[i]),LCD_CHR)
            elif LcdCmd.Blank == cmd:
                await self._blank()
            elif LcdCmd.BacklightSet == cmd:
                await self._set_backlight(arg1)
            self._queue.task_done()

    def stop(self):
        self._is_task_active = False
    
    async def _init(self):
        logging.info("Initialization start")
        self._init_gpio()
        await self._init_lcd()
        logging.info("Initialization done")

    def _init_gpio(self):
        GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
        GPIO.setup(LCD_E, GPIO.OUT)  # E
        GPIO.setup(LCD_RS, GPIO.OUT) # RS
        GPIO.setup(LCD_D4, GPIO.OUT) # DB4
        GPIO.setup(LCD_D5, GPIO.OUT) # DB5
        GPIO.setup(LCD_D6, GPIO.OUT) # DB6
        GPIO.setup(LCD_D7, GPIO.OUT) # DB7
        GPIO.setup(LED_ON, GPIO.OUT) # Backlight enable

    async def _init_lcd(self):
        # Initialise display
        await self._send_byte(0x33,LCD_CMD) # 110011 Initialise
        await self._send_byte(0x32,LCD_CMD) # 110010 Initialise
        await self._send_byte(0x06,LCD_CMD) # 000110 Cursor move direction
        await self._send_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
        await self._send_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
        await self._send_byte(0x01,LCD_CMD) # 000001 Clear display
        await asyncio.sleep(LcdDisplay.E_DELAY)

    async def _blank(self):
        await self._send_byte(0x01, LCD_CMD)

    async def _set_backlight(self, flag):
        # Toggle backlight on-off-on
        GPIO.output(LED_ON, flag)

    async def _change_active_line(self, line):
        await self._send_byte(line, LCD_CMD)

    async def _send_byte(self, bits, mode):
        # Send byte to data pins
        # bits = data
        # mode = True  for character
        #        False for command
        GPIO.output(LCD_RS, mode) # RS
        # High bits
        GPIO.output(LCD_D4, False)
        GPIO.output(LCD_D5, False)
        GPIO.output(LCD_D6, False)
        GPIO.output(LCD_D7, False)
        if bits&0x10==0x10:
            GPIO.output(LCD_D4, True)
        if bits&0x20==0x20:
            GPIO.output(LCD_D5, True)
        if bits&0x40==0x40:
            GPIO.output(LCD_D6, True)
        if bits&0x80==0x80:
            GPIO.output(LCD_D7, True)
        # Toggle 'Enable' pin
        await self._toggle_enable()
        # Low bits
        GPIO.output(LCD_D4, False)
        GPIO.output(LCD_D5, False)
        GPIO.output(LCD_D6, False)
        GPIO.output(LCD_D7, False)
        if bits&0x01==0x01:
            GPIO.output(LCD_D4, True)
        if bits&0x02==0x02:
            GPIO.output(LCD_D5, True)
        if bits&0x04==0x04:
            GPIO.output(LCD_D6, True)
        if bits&0x08==0x08:
            GPIO.output(LCD_D7, True)
        # Toggle 'Enable' pin
        await self._toggle_enable()

    async def _toggle_enable(self):
        # Toggle enable
        await asyncio.sleep(LcdDisplay.E_DELAY)
        GPIO.output(LCD_E, True)
        await asyncio.sleep(LcdDisplay.E_PULSE)
        GPIO.output(LCD_E, False)
        await asyncio.sleep(LcdDisplay.E_DELAY)
    
async def main():
    logging.basicConfig(format='LCD %(levelname)s: %(message)s', level=logging.INFO)
    display = LcdDisplay()
    asyncio.create_task(display.run())

    try:
        logging.info("Indicate start via backlight flash")
        display.set_backlight(True)
        await asyncio.sleep(0.5)
        display.set_backlight(False)
        await asyncio.sleep(0.5)
        display.set_backlight(True)
        await asyncio.sleep(0.5)

        logging.info("Starting example message loop")
        while True:
            # Send some centred test
            display.send_string("--------------------", LcdDisplay.LCD_LINE_1, LcdLineStyle.Centred)
            display.send_string("Rasbperry Pi", LcdDisplay.LCD_LINE_2, LcdLineStyle.Centred)
            display.send_string("K(V)M", LcdDisplay.LCD_LINE_3, LcdLineStyle.Centred)
            display.send_string("--------------------", LcdDisplay.LCD_LINE_4, LcdLineStyle.Centred)
        
            await asyncio.sleep(3)

            lt = time.localtime(time.time())
            time_str = f"{lt.tm_mday:02}.{lt.tm_mon:02}.{lt.tm_year}     {lt.tm_hour:02}:{lt.tm_min:02}"
            display.send_string("RPi - K(V)M", LcdDisplay.LCD_LINE_1, LcdLineStyle.Centred)
            display.send_string(time_str, LcdDisplay.LCD_LINE_2, LcdLineStyle.Centred)
            display.send_string("", LcdDisplay.LCD_LINE_3, LcdLineStyle.Centred)
            display.send_string("", LcdDisplay.LCD_LINE_4, LcdLineStyle.Centred)

            await asyncio.sleep(3)
            display.blank()
            await asyncio.sleep(3)
    except KeyboardInterrupt:
        raise
    finally:
        display.cleanup()
 
if __name__ == '__main__':
    asyncio.run( main() )
