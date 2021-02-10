# USB HID device report descriptors

To get all usb devices listed execute `lsusb`. In the following we concentrait on the Logitech device. It will be identified in the follwoing via its Bus (001) und Device (008) number:

```bash
$ lsusb
Bus 001 Device 008: ID 046d:c52b Logitech, Inc. Unifying Receiver
Bus 001 Device 007: ID 17ef:608c Lenovo
Bus 001 Device 003: ID 0424:ec00 Standard Microsystems Corp. SMSC9512/9514 Fast Ethernet Adapter
Bus 001 Device 002: ID 0424:9514 Standard Microsystems Corp. SMC9514 Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

Get the USB HID device report descriptors in `hex` for a device use the standard linux tool `usbhid-dump`([docu link](https://github.com/DIGImend/usbhid-dump)):

```bash
$ sudo usbhid-dump -s 001:008
001:008:002:DESCRIPTOR         1609787704.066087
 06 00 FF 09 01 A1 01 85 10 95 06 75 08 15 00 26
 FF 00 09 01 81 00 09 01 91 00 C0 06 00 FF 09 02
 A1 01 85 11 95 13 75 08 15 00 26 FF 00 09 02 81
 00 09 02 91 00 C0 06 00 FF 09 04 A1 01 85 20 95
 0E 75 08 15 00 26 FF 00 09 41 81 00 09 41 91 00
 85 21 95 1F 09 42 81 00 09 42 91 00 C0

001:008:001:DESCRIPTOR         1609787704.069870
 05 01 09 02 A1 01 85 02 09 01 A1 00 95 10 75 01
 15 00 25 01 05 09 19 01 29 10 81 02 95 02 75 0C
 16 01 F8 26 FF 07 05 01 09 30 09 31 81 06 95 01
 75 08 15 81 25 7F 09 38 81 06 95 01 05 0C 0A 38
 02 81 06 C0 C0 05 0C 09 01 A1 01 85 03 95 02 75
 10 15 01 26 FF 02 19 01 2A FF 02 81 00 C0 05 01
 09 80 A1 01 85 04 95 01 75 02 15 01 25 03 09 82
 09 81 09 83 81 00 75 06 81 03 C0 06 BC FF 09 88
 A1 01 85 08 95 01 75 08 15 01 26 FF 00 19 01 29
 FF 81 00 C0

001:008:000:DESCRIPTOR         1609787704.072736
 05 01 09 06 A1 01 95 08 75 01 15 00 25 01 05 07
 19 E0 29 E7 81 02 81 03 95 05 05 08 19 01 29 05
 91 02 95 01 75 03 91 01 95 06 75 08 15 00 26 FF
 00 05 07 19 00 2A FF 00 81 00 C0
```

`hidrd-convert`([docu link](https://github.com/DIGImend/hidrd)) converts the hex dump into HID specification example format. Install it via `sudo apt-get install hidrd`.

```bash
$ sudo usbhid-dump -a1:8 -i0 | grep -v : | xxd -r -p | hidrd-convert -o spec
Usage Page (Desktop),               ; Generic desktop controls (01h)
Usage (Keyboard),                   ; Keyboard (06h, application collection)
Collection (Application),
    Report Count (8),
    Report Size (1),
    Logical Minimum (0),
    Logical Maximum (1),
    Usage Page (Keyboard),          ; Keyboard/keypad (07h)
    Usage Minimum (KB Leftcontrol), ; Keyboard left control (E0h, dynamic value)
    Usage Maximum (KB Right GUI),   ; Keyboard right GUI (E7h, dynamic value)
    Input (Variable),
    Input (Constant, Variable),
    Report Count (5),
    Usage Page (LED),               ; LEDs (08h)
    Usage Minimum (01h),
    Usage Maximum (05h),
    Output (Variable),
    Report Count (1),
    Report Size (3),
    Output (Constant),
    Report Count (6),
    Report Size (8),
    Logical Minimum (0),
    Logical Maximum (255),
    Usage Page (Keyboard),          ; Keyboard/keypad (07h)
    Usage Minimum (None),           ; No event (00h, selector)
    Usage Maximum (FFh),
    Input,
End Collection

$ sudo usbhid-dump -a1:8 -i1 | grep -v : | xxd -r -p | hidrd-convert -o spec
Usage Page (Desktop),                   ; Generic desktop controls (01h)
Usage (Mouse),                          ; Mouse (02h, application collection)
Collection (Application),
    Report ID (2),
    Usage (Pointer),                    ; Pointer (01h, physical collection)
    Collection (Physical),
        Report Count (16),
        Report Size (1),
        Logical Minimum (0),
        Logical Maximum (1),
        Usage Page (Button),            ; Button (09h)
        Usage Minimum (01h),
        Usage Maximum (10h),
        Input (Variable),
        Report Count (2),
        Report Size (12),
        Logical Minimum (-2047),
        Logical Maximum (2047),
        Usage Page (Desktop),           ; Generic desktop controls (01h)
        Usage (X),                      ; X (30h, dynamic value)
        Usage (Y),                      ; Y (31h, dynamic value)
        Input (Variable, Relative),
        Report Count (1),
        Report Size (8),
        Logical Minimum (-127),
        Logical Maximum (127),
        Usage (Wheel),                  ; Wheel (38h, dynamic value)
        Input (Variable, Relative),
        Report Count (1),
        Usage Page (Consumer),          ; Consumer (0Ch)
        Usage (AC Pan),                 ; AC pan (0238h, linear control)
        Input (Variable, Relative),
    End Collection,
End Collection,
Usage Page (Consumer),                  ; Consumer (0Ch)
Usage (Consumer Control),               ; Consumer control (01h, application collection)
Collection (Application),
    Report ID (3),
    Report Count (2),
    Report Size (16),
    Logical Minimum (1),
    Logical Maximum (767),
    Usage Minimum (Consumer Control),   ; Consumer control (01h, application collection)
    Usage Maximum (02FFh),
    Input,
End Collection,
Usage Page (Desktop),                   ; Generic desktop controls (01h)
Usage (Sys Control),                    ; System control (80h, application collection)
Collection (Application),
    Report ID (4),
    Report Count (1),
    Report Size (2),
    Logical Minimum (1),
    Logical Maximum (3),
    Usage (Sys Sleep),                  ; System sleep (82h, one-shot control)
    Usage (Sys Power Down),             ; System power down (81h, one-shot control)
    Usage (Sys Wake Up),                ; System wake up (83h, one-shot control)
    Input,
    Report Size (6),
    Input (Constant, Variable),
End Collection,
Usage Page (FFBCh),                     ; FFBCh, vendor-defined
Usage (88h),
Collection (Application),
    Report ID (8),
    Report Count (1),
    Report Size (8),
    Logical Minimum (1),
    Logical Maximum (255),
    Usage Minimum (01h),
    Usage Maximum (FFh),
    Input,
End Collection

$ sudo usbhid-dump -a1:8 -i2 | grep -v : | xxd -r -p | hidrd-convert -o spec
Usage Page (FF00h),         ; FF00h, vendor-defined
Usage (01h),
Collection (Application),
    Report ID (16),
    Report Count (6),
    Report Size (8),
    Logical Minimum (0),
    Logical Maximum (255),
    Usage (01h),
    Input,
    Usage (01h),
    Output,
End Collection,
Usage Page (FF00h),         ; FF00h, vendor-defined
Usage (02h),
Collection (Application),
    Report ID (17),
    Report Count (19),
    Report Size (8),
    Logical Minimum (0),
    Logical Maximum (255),
    Usage (02h),
    Input,
    Usage (02h),
    Output,
End Collection,
Usage Page (FF00h),         ; FF00h, vendor-defined
Usage (04h),
Collection (Application),
    Report ID (32),
    Report Count (14),
    Report Size (8),
    Logical Minimum (0),
    Logical Maximum (255),
    Usage (41h),
    Input,
    Usage (41h),
    Output,
    Report ID (33),
    Report Count (31),
    Usage (42h),
    Input,
    Usage (42h),
    Output,
End Collection
```

`lsusb -v` gives the detailed explained information of the device descriptor of a USB device:

```bash
$ lsusb -s 001:008 -v

Bus 001 Device 008: ID 046d:c52b Logitech, Inc. Unifying Receiver
Couldn't open device, some information will be missing
Device Descriptor:
  bLength                18
  bDescriptorType         1
  bcdUSB               2.00
  bDeviceClass            0
  bDeviceSubClass         0
  bDeviceProtocol         0
  bMaxPacketSize0         8
  idVendor           0x046d Logitech, Inc.
  idProduct          0xc52b Unifying Receiver
  bcdDevice           12.11
  iManufacturer           1
  iProduct                2
  iSerial                 0
  bNumConfigurations      1
  Configuration Descriptor:
    bLength                 9
    bDescriptorType         2
    wTotalLength       0x0054
    bNumInterfaces          3
    bConfigurationValue     1
    iConfiguration          4
    bmAttributes         0xa0
      (Bus Powered)
      Remote Wakeup
    MaxPower               98mA
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        0
      bAlternateSetting       0
      bNumEndpoints           1
      bInterfaceClass         3 Human Interface Device
      bInterfaceSubClass      1 Boot Interface Subclass
      bInterfaceProtocol      1 Keyboard
      iInterface              0
        HID Device Descriptor:
          bLength                 9
          bDescriptorType        33
          bcdHID               1.11
          bCountryCode            0 Not supported
          bNumDescriptors         1
          bDescriptorType        34 Report
          wDescriptorLength      59
         Report Descriptors:
           ** UNAVAILABLE **
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x81  EP 1 IN
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0008  1x 8 bytes
        bInterval               8
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        1
      bAlternateSetting       0
      bNumEndpoints           1
      bInterfaceClass         3 Human Interface Device
      bInterfaceSubClass      1 Boot Interface Subclass
      bInterfaceProtocol      2 Mouse
      iInterface              0
        HID Device Descriptor:
          bLength                 9
          bDescriptorType        33
          bcdHID               1.11
          bCountryCode            0 Not supported
          bNumDescriptors         1
          bDescriptorType        34 Report
          wDescriptorLength     148
         Report Descriptors:
           ** UNAVAILABLE **
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x82  EP 2 IN
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0008  1x 8 bytes
        bInterval               2
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        2
      bAlternateSetting       0
      bNumEndpoints           1
      bInterfaceClass         3 Human Interface Device
      bInterfaceSubClass      0
      bInterfaceProtocol      0
      iInterface              0
        HID Device Descriptor:
          bLength                 9
          bDescriptorType        33
          bcdHID               1.11
          bCountryCode            0 Not supported
          bNumDescriptors         1
          bDescriptorType        34 Report
          wDescriptorLength      93
         Report Descriptors:
           ** UNAVAILABLE **
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x83  EP 3 IN
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0020  1x 32 bytes
        bInterval               2
```

## Create my own hid descriptor for keyboard + mouse with horizontal wheel

HID descriptor of a basic mouse:

```bash
05010902a10185020901a100950575010509190129051500250181029501750381017508950305010930093109381581257f8106c0c0
```

Translaited spec of a basic mouse with its plane hex values on the side:

```bash
# Basic mouse detail
0501    Usage Desktop 
0902    Usage Mouse
a101    Collection Application
8502        Report ID (2)
0901        Usage (Pointer),                ; Pointer (01h, physical collection)
a100        Collection (Physical),
9505            Report Count (5),
7501            Report Size (1),
0509            Usage Page (Button),        ; Button (09h)
1901            Usage Minimum (01h),
2905            Usage Maximum (05h),
1500            Logical Minimum (0),
2501            Logical Maximum (1),
8102            Input (Variable),
9501            Report Count (1),
7503            Report Size (3),
8101            Input (Constant),
7508            Report Size (8),
9503            Report Count (3),
0501            Usage Page (Desktop),       ; Generic desktop controls (01h)
0930            Usage (X),                  ; X (30h, dynamic value)
0931            Usage (Y),                  ; Y (31h, dynamic value)
0938            Usage (Wheel),              ; Wheel (38h, dynamic value)
1581            Logical Minimum (-127),
257f            Logical Maximum (127),
8106            Input (Variable, Relative),
c0            End Collection
c0      End Collection
```

Append the horizontal wheel description:

- Report Size (8),
- Report Count (1),
- Usage Page (Consumer),          ; Consumer (0Ch)
- Usage (AC Pan),                 ; AC pan (0238h, linear control)
- Logical Minimum (-127),
- Logical Maximum (127),
- Input (Variable, Relative),

```bash
# Mouse detail with added horizontal wheel support
0501    Usage Desktop
0902    Usage Mouse
a101    Collection Application
8502        Report ID (2)
0901        Usage (Pointer),                ; Pointer (01h, physical collection)
a100        Collection (Physical),
9505            Report Count (5),
7501            Report Size (1),
0509            Usage Page (Button),        ; Button (09h)
1901            Usage Minimum (01h),
2905            Usage Maximum (05h),
1500            Logical Minimum (0),
2501            Logical Maximum (1),
8102            Input (Variable),
9501            Report Count (1),
7503            Report Size (3),
8101            Input (Constant),
7508            Report Size (8),
9503            Report Count (3),
0501            Usage Page (Desktop),       ; Generic desktop controls (01h)
0930            Usage (X),                  ; X (30h, dynamic value)
0931            Usage (Y),                  ; Y (31h, dynamic value)
0938            Usage (Wheel),              ; Wheel (38h, dynamic value)
1581            Logical Minimum (-127),
257f            Logical Maximum (127),
8106            Input (Variable, Relative),
7508            Report Size (8),
9501            Report Count (1),
050C            Usage Page (Consumer),          ; Consumer (0Ch)
0A3802          Usage (AC Pan),                 ; AC pan (0238h, linear control)
1581            Logical Minimum (-127),
257f            Logical Maximum (127),
8106            Input (Variable, Relative),
c0            End Collection
c0      End Collection
```

### Combine the descriptors

```bash
# Complete with basic keyboard + basic mouse (point of beginning)
05010906a101850175019508050719e029e715002501810295017508810395057501050819012905910295017503910395067508150026ff000507190029ff8100c005010902a10185020901a100950575010509190129051500250181029501750381017508950305010930093109381581257f8106c0c0

# Keyboard (basic)
05010906a101850175019508050719e029e715002501810295017508810395057501050819012905910295017503910395067508150026ff000507190029ff8100c0

# Mouse (basic)
05010902a10185020901a100950575010509190129051500250181029501750381017508950305010930093109381581257f8106c0c0

# Mouse with H-Wheel
05010902a10185020901a100950575010509190129051500250181029501750381017508950305010930093109381581257f810675089501050C0A38021581257f8106c0c0

# Keyboard + Mouse with H-Wheel
05010906a101850175019508050719e029e715002501810295017508810395057501050819012905910295017503910395067508150026ff000507190029ff8100c005010902a10185020901a100950575010509190129051500250181029501750381017508950305010930093109381581257f810675089501050C0A38021581257f8106c0c0
```
