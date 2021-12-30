import re
import sys
import usb.core
import usb.util
from time import sleep

COMMANDS = {
    "AT":  1,  "API": 3,  "APR": 4,  "APWE": 11, "APFU": 15,
    "AMQ": 20, "AMW": 24, "AMR": 25, "AMBE": 28, "AMWD": 29, "AFCIO": 30,
}

# https://www.beyondlogic.org/usbnutshell/usb6.shtml
BM_REQUEST_TYPES = {
  "vendor": 0x40,
  "device_to_host_AND_vendor": 0xC0
}

# Grab the first available WebFPGA device
def get_device():
    device = usb.core.find(idVendor=0x16D0, idProduct=0x0e6c)
    # print(device)
    if device is None:
        raise ValueError("Device not found")
    return device

# Issue a command to the USB device
def issue_command(device, command, wIndex=0, data=None):
    # Assemble USB xfer out
    bmRequestType = BM_REQUEST_TYPES["vendor"]
    bmRequest = 250 # user-defined by our firmware
    wValue = COMMANDS[command]

    # Run request
    bytes_written = device.ctrl_transfer(bmRequestType, bmRequest, wValue, wIndex, data)

    print(command + ": ", end="")
    return bytes_written

def expect(device, expected):
    bmRequestType = BM_REQUEST_TYPES["device_to_host_AND_vendor"]
    bmRequest = 249 # user-defined by our firmware
    wValue = 0x70   # our command
    wIndex = 0x81   # data index for command
    wLength = 128   # bytes to read

    ret = device.ctrl_transfer(bmRequestType, bmRequest, wValue, wIndex, wLength)
    result = "".join([chr(x) for x in ret]).rstrip(" \t\r\n\0")
    match = re.match(expected, result)

    if match:
        print(result)
        return result.strip("\00\0A")
    else:
        print(result + "(wanted " + expected + ")")

def handshake(device, command, expected, wIndex=0, data=None):
    issue_command(device, command, wIndex, data)
    return expect(device, expected)

# Set a MCU bit to 0 or 1
def set_bit(dev, bit, value):
    # toggle --> offset 0, set 1 --> offset 4, set 0 --> offset 8
    bit += (4 if (value == 1) else 8)
    handshake(dev, "AFCIO", "^Done", wIndex=bit)

def SetBitstring(bitstring):
    # valid bitstring
    match = re.match("[01][01][01][01]", bitstring)
    if not match:
        print(f"error: bitstring is invalid: {bitstring}")
        print( "       Try something like '0101'")
        sys.exit(1)

    # open usb device and validate connection
    print("Opening USB device...")
    dev = get_device()
    handshake(dev, "AT", "Hi")

    # set bits
    print("\nSetting bits...")
    for bit in range(len(bitstring)):
        val = int(bitstring[bit])
        set_bit(dev, bit, val)
