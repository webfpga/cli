import usb.core
import usb.util

COMMANDS = {
    "AT":  1,  "API": 3,  "APR": 4,  "APWE": 11, "APFU": 15,
    "AMQ": 20, "AMW": 24, "AMR": 25, "AMBE": 28, "AMWD": 29, "AFCIO": 30,
}

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

def expect(device, expected, data=None):        
    ret = device.ctrl_transfer(0xC0, 249, 0x70, 0x81, 128)
    result = "".join([chr(x) for x in ret]).rstrip(" \t\r\n\0")
    match = re.match(expected, result)

    if match:
        print(result)
        return result.strip("\00\0A")
    else:
        print(result + "(wanted " + expected + ")")

def handshake(device, command, expected, data=None):
    issue_command(device, command, data)
    return expect(device, expected, data)

# Set a MCU bit to 0 or 1
def SetBit(bit, value):
    print("Opening USB device...")
    dev = get_device()

    print("Testing connection...")
    handshake(device, "AT", "Hi")

    print("Setting bit...")
    handshake(device, "AFCIO", "^Done", bit)
