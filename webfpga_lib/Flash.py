#!/usr/bin/python3

import Compress

import usb.core
import usb.util
import re
import sys
import textwrap

COMMANDS = {
    "AT":  1,  "API": 3,  "APR": 4,  "APWE": 11, "APFU": 15,
    "AMQ": 20, "AMW": 24, "AMR": 25, "AMBE": 28, "AMWD": 29, "AFCIO": 30
}

# Print the USB devices verbosely (mainly for debug, info spouting)
def print_devices(devices):
    for cfg in devices:
        sys.stdout.write("Config " + str(cfg.bConfigurationValue) + "\n")
        for intf in cfg:
            sys.stdout.write("\tInterface " + \
                str(intf.bInterfaceNumber) + "," + \
                str(intf.bAlternateSetting) + "\n")

            for ep in intf:
                sys.stdout.write("\t\tEndpoint " + \
                str(ep.bEndpointAddress) + "\n")

# Grab the first available WebFPGA device
def get_first_device():
    devices = usb.core.find(idVendor=0x16D0, idProduct=0x0e6c)
    if devices is None:
        raise ValueError("Device not found")
    print_devices(devices)
    return devices[0]

# Issue a command to the USB device
def issue_command(device, command, data):
    code = COMMANDS[command]
    bytes_written = device.ctrl_transfer(0x40, 250, commandcode, 0, data)
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

def handshake(command, expected):
    issue_command(command, None)
    return expect(expected)

#   def prepare(self):
#       self.handshake("AT", "Hi")
#           self.handshake("API", "C_WEBUSB|CWEBUSB+")
#           self.handshake("APR", "000921|01010(4|5|6|7)");
#           print("Found programmer.")

#           print("Checking for FPGA module and its flash configuration...")
#           self.handshake("APWE", "wren")
#           amq = self.handshake("AMQ", ".*")

#           assert len(amq) >= 9, "Bad AMQ response, too short."
#           assert amq[0] == "S", "Flash device not supported."
#           assert amq[6] == "H", "Flash device has bad Cascadia header."

#   def erase(self):
#       self.handshake("AMBE", "DONE")
#           amq = self.handshake("AMQ", ".*")

#           assert len(amq) >= 9, "Bad AMQ response, too short."
#           assert amq[0] == "S", "Flash device not supported."
#           assert amq[5] == "W", "Flash device is write protected."
#           assert amq[6] == "H", "Flash device has bad Cascadia header."
#           assert amq[8] == "E", "Flash device is not erased."

#   def flash(self, f):
#       self.handshake("AMW", "OK")
#           offset = 0;
#           self.watch(False)
#           while True:
#               header = f.read(1)
#                   if len(header) == 0:
#                       break
#                   l = header[0]
#                   if (l & 0x80) != 0:
#                       l = l & 0x7F
#                   body = f.read(l-1);
#                   assert len(body) == l-1, "Short block!"

#                   # print each tx block
#                   for line in textwrap.wrap(body.hex(), 40):
#                       print(line)

#                   # transmit the block
#                   combined = bytearray(header)
#                   combined.extend(body)
#                   res = self.issue("AMWD", combined)
#                   self.expect(".*")
#                   offset = offset + l

#                   # print the device's response
#                   print("RESPONSE =>", res, "\n");

#                   # Removed progress bar for debugging.
#                   # Will be added back in the future....
#                   #self.progress.advance(offset)
#           #self.progress.advance(None)
#           print("Flashing complete")

def Flash(x):
    print("Opening USB device...")
    dev = get_first_device()
