#!/usr/bin/python3

import lib.Compress

import usb.core
import usb.util
import re
import sys
import textwrap

def Flash(x):
    print("FLASH")
    print(x)

class Progress:
        def __init__(self):
                pass

        def advance(self, offset):
                pass

class ProgressDots(Progress):

        def __init__(self, limit=20):
                self.limit = 20
                self.count = 0

        def advance(self, offset):
                if offset is not None:
                        print('.', flush=True, end='')
                        self.count = self.count + 1
                if self.count == self.limit or offset is None:
                        print('');
                        self.count = 0

class ProgressBar(Progress):

        def __init__(self, modulus=500):
                self.modulus = modulus;
                self.previous = -1
                self.here = 0
                self.spinner_done = '!'
                self.spinner_sequence = '-/|\\'

        def advance(self, offset):
                if offset is None:
                        token = self.spinner_done
                        report = self.here
                        out = True
                else:
                        self.here = offset
                        if (self.here // self.modulus) == (self.previous // self.modulus):
                                out = False
                        else:
                                out = True
                                tok = (self.here // self.modulus) % len(self.spinner_sequence)
                                token = self.spinner_sequence[tok:tok+1]
                                report = offset
                if out:
                        print("\r{0:6d} {1:s}".format(report, token), flush=True, end='')
                if offset is None:
                        print('')
                self.previous = self.here

class Flasher:

        def __init__(self):
                self.commandmap = {
                        "AT":   1,  "API":  3,  "APR":  4,  "APWE": 11, "APFU": 15,
                        "AMQ":  20, "AMW":  24, "AMR":  25, "AMBE": 28, "AMWD": 29,
                        "AFCIO": 30
                }
                self.dev = usb.core.find(idVendor=0x16D0, idProduct=0x0e6c)
                if self.dev is None:
                        raise ValueError('Device not found')
                # Removed progress bar for debugging.
                # Will be added back in the future....
                #self.progress = ProgressBar()
                self.monitor = True

        def watch(self, it=True):
                self.monitor = it

        def iterate(self):
                for cfg in self.dev:
                        sys.stdout.write("Config " + str(cfg.bConfigurationValue) + '\n')
                        for intf in cfg:
                                sys.stdout.write('\tInterface ' + \
                                                 str(intf.bInterfaceNumber) + \
                                                 ',' + \
                                                 str(intf.bAlternateSetting) + \
                                                 '\n')
                                for ep in intf:
                                        sys.stdout.write('\t\tEndpoint ' + \
                                                         str(ep.bEndpointAddress) + \
                                                         '\n')


        def issue(self, command, data):
                commandcode = self.commandmap[command]
                written = self.dev.ctrl_transfer(0x40, 250, commandcode, 0, data)
                if self.monitor:
                        print(command + ": ", end='');
                return written
                
        def expect(self, expected):        
                ret = self.dev.ctrl_transfer(0xC0, 249, 0x70, 0x81, 128)
                result = ''.join([chr(x) for x in ret]).rstrip(' \t\r\n\0')
                match = re.match(expected, result)
                if match:
                        if self.monitor:
                                print(result)
                        return result.strip('\00\0A')
                else:
                        if self.monitor:
                                print(result + "(wanted " + expected + ")")
                        assert(0)

        def handshake(self, command, expected):
                self.issue(command, None)
                return self.expect(expected)

        def prepare(self):
                self.handshake("AT", "Hi")
                self.handshake("API", "C_WEBUSB|CWEBUSB+")
                self.handshake("APR", "000921|01010(4|5|6|7)");
                print("Found programmer.")

                print("Checking for FPGA module and its flash configuration...")
                self.handshake("APWE", "wren")
                amq = self.handshake("AMQ", ".*")

                assert len(amq) >= 9, "Bad AMQ response, too short."
                assert amq[0] == "S", "Flash device not supported."
                assert amq[6] == "H", "Flash device has bad Cascadia header."

        def erase(self):
                self.handshake("AMBE", "DONE")
                amq = self.handshake("AMQ", ".*")

                assert len(amq) >= 9, "Bad AMQ response, too short."
                assert amq[0] == "S", "Flash device not supported."
                assert amq[5] == "W", "Flash device is write protected."
                assert amq[6] == "H", "Flash device has bad Cascadia header."
                assert amq[8] == "E", "Flash device is not erased."
                
        def flash(self, f):
                self.handshake("AMW", "OK")
                offset = 0;
                self.watch(False)
                while True:
                        header = f.read(1)
                        if len(header) == 0:
                                break
                        l = header[0]
                        if (l & 0x80) != 0:
                                l = l & 0x7F
                        body = f.read(l-1);
                        assert len(body) == l-1, "Short block!"

                        # print each tx block
                        for line in textwrap.wrap(body.hex(), 40):
                            print(line)

                        # transmit the block
                        combined = bytearray(header)
                        combined.extend(body)
                        res = self.issue("AMWD", combined)
                        self.expect(".*")
                        offset = offset + l

                        # print the device's response
                        print("RESPONSE =>", res, "\n");

                        # Removed progress bar for debugging.
                        # Will be added back in the future....
                        #self.progress.advance(offset)
                #self.progress.advance(None)
                print("Flashing complete")

def main():
        if len(sys.argv) == 2:
                filename = sys.argv[1]
        else:
                filename = "bitstream.bin"

        flasher = Flasher()
        flasher.iterate()
        flasher.prepare()

        with open(filename, "rb") as f:
                  flasher.erase()
                  flasher.flash(f)

if __name__== "__main__":
          main()
