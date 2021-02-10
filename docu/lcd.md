# LCD Module

Read the [full article](https://www.raspberrypi-spy.co.uk/2012/08/20x4-lcd-module-control-using-python/) how to wire and setup the lcd module with the raspberry pi by [raspberrypi-spy.co.uk](https://www.raspberrypi-spy.co.uk).

## LCD Module Hardware

The pinout of the lcd module is :

1. Ground
2. VCC (Usually +5V)
3. Contrast adjustment (VO)
4. Register Select (RS): RS=0: Command, RS=1: Data
5. Read/Write (R/W): R/W=0: Write, R/W=1: Read
6. Enable
7. Bit 0 (Not required in 4-bit operation)
8.  Bit 1 (Not required in 4-bit operation)
9.  Bit 2 (Not required in 4-bit operation)
10. Bit 3 (Not required in 4-bit operation)
11. Bit 4
12. Bit 5
13. Bit 6
14. Bit 7
15. LED Backlight Anode (+)
16. LED Backlight Cathode (-)

## LCD - Raspberry Pi wireing

In the following picture the wireing is shown:

![wirering picture](https://www.raspberrypi-spy.co.uk/wp-content/uploads/2012/08/HD44780-LCD-Advanced-2.png)

The following pins are connected in detail:

LCD-Pin | Function | Pi-Function | Pi-Pin
-- | --- | --- | ---
01 | GND | GND | P1-06
02 | +5V | +5V | P1-02
03 | Contrast
04 | RS | GPIO7 | P1-26
05 | RW | GND | P1-06
06 | E | GPIO8 | P1-24
07 | Data 0
08 | Data 1
09 | Data 2
10 | Data 3
11 | Data 4 | GPIO25 | P1-22
12 | Data 5 | GPIO24 | P1-18
13 | Data 6 | GPIO23 | P1-16
14 | Data 7 | GPIO18 | P1-12
15 | +5V via 560 ohm
16 | GND | | P1-06
