#!/usr/bin/python3

from webfpga.Compress import compress

import usb.core
import usb.util
import re
import sys
import textwrap

COMMANDS = {
    "AT":  1,  "API": 3,  "APR": 4,  "APWE": 11, "APFU": 15,
    "AMQ": 20, "AMW": 24, "AMR": 25, "AMBE": 28, "AMWD": 29, "AFCIO": 30
}

# Main flash routine:
# Flash device with bitstream
# If the bitstream is uncompressed, then compress it
def Flash(bitstream):
    print("Opening USB device...")
    dev = get_device()

    print("\nPreparing device for flashing...")
    prepare(dev)

    print("\nErasing device...")
    erase(dev)

    print("\nFlashing device...")
    flash(dev, compress(bitstream))

# Grab the first available WebFPGA device
def get_device():
    device = usb.core.find(idVendor=0x16D0, idProduct=0x0e6c)
    # print(device)
    if device is None:
        raise ValueError("Device not found")
    return device

# Issue a command to the USB device
def issue_command(device, command, data):
    code = COMMANDS[command]
    bytes_written = device.ctrl_transfer(0x40, 250, code, 0, data)
    print(command + ": ", end="")
    return bytes_written

def expect(device, expected):        
    ret = device.ctrl_transfer(0xC0, 249, 0x70, 0x81, 128)
    result = "".join([chr(x) for x in ret]).rstrip(" \t\r\n\0")
    match = re.match(expected, result)

    if match:
        print(result)
        return result.strip("\00\0A")
    else:
        print(result + "(wanted " + expected + ")")

def handshake(device, command, expected):
    issue_command(device, command, None)
    return expect(device, expected)

def prepare(device):
    handshake(device, "AT", "Hi")
    handshake(device, "API", "C_WEBUSB|CWEBUSB+")
    handshake(device, "APR", "000921|01010(4|5|6|7)");
    print("Found programmer.")

    print("Checking for FPGA module and its flash configuration...")
    handshake(device, "APWE", "wren")
    amq = handshake(device, "AMQ", ".*")

    assert len(amq) >= 9, "Bad AMQ response, too short."
    assert amq[0] == "S", "Flash device not supported."
    assert amq[6] == "H", "Flash device has bad Cascadia header."

def erase(device):
    handshake(device, "AMBE", "DONE")
    amq = handshake(device, "AMQ", ".*")

    assert len(amq) >= 9, "Bad AMQ response, too short."
    assert amq[0] == "S", "Flash device not supported."
    assert amq[5] == "W", "Flash device is write protected."
    assert amq[6] == "H", "Flash device has bad Cascadia header."
    assert amq[8] == "E", "Flash device is not erased."

def flash(device, buf):
    handshake(device, "AMW", "OK")

    idx = 0
    while idx < len(buf):
        # Read the block size,
        # then and use that to slice a block
        block_size = buf[idx]
        block = buf[idx:idx+block_size]
        idx += block_size

        # transmit the block
        res = issue_command(device, "AMWD", block)
        expect(device, ".*")

        # print the device's response
        print("RESPONSE =>", res, "\n");
