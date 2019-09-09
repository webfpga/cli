# webfpga/cli

Python port of the WebFPGA CLI. As of right now, only bitstream
flashing is supported.

## Update
Bitstream downloading and compression is nearly supported! (9/8/2019)

## Example
Use the Node.js utility to synthesize and create a bitstream. Then, use the
Python utility to flash the device.
```console
# Install the old Node.js utility to synthesize the HDL
$ npm install -g webfpga-cli
$ webfpga synth blinky.v
$ ls
bitstream.bin

# Fetch the new Python utility to flash your device
$ git clone https://github.com/webfpga/cli
$ cp cli/flash.py .
$ pip install pyusb
$ python flash.py bitstream.bin
```
