#!/usr/bin/python3

from webfpga.Compress import compress
from webfpga.Utilities import *

import usb.core
import usb.util
import re
import sys
import textwrap

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
        res = issue_command(device, "AMWD", wIndex=0, data=block)
        expect(device, ".*")

        # print the device's response
        print("RESPONSE =>", res, "\n");
