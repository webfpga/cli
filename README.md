# webfpga/cli
[![PyPI version](https://badge.fury.io/py/webfpga.svg)](https://badge.fury.io/py/webfpga)

**Python migration is complete! This repository is feature-complete with the web
IDE.**

Welcome to the official command-line utility for WebFPGA compatible devices.
If you are unfamiliar with WebFPGA, please checkout the homepage
([webfpga.io](https://webfpga.io)) or our Kickstarter
([webfpga.io/kickstarter](https://webfpga.io/kickstarter)).

This utility provides access to the official backend for Verilog synthesis.
It also provides flashing capability for the official WebFPGA family of
boards ([store.webfpga.io](https://store.webfpga.io)). You are free to use
bitstreams sourced from our tools, Lattice's iCECube, or IceStorm. They
should all work.

## Installation
```console
$ pip install webfpga
$ webfpga --help
Usage: webfpga [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  flash  Flash the first connected WebFPGA device
  synth  Synthesize one or more input Verilog files and save the bitstream
```

## Example
The utility is fairly simply to use once installed. Simply
synthesize one or more Verilog source files to produce a bitstream.
Then, feed that bitstream into `webfpga flash` to load the binary
onto your local device. E.g.
`webfpga synth input.v -o bitstream.bin && webfpga flash bitstream.bin`.
By default, `webfpga synth` will save the bitstream as `bitstream.bin`, but
you can use `-o` to specify a different filename.

```console
$ curl -O https://beta.webfpga.io/static/WF_blinky.v
$ webfpga synth WF_blinky.v
WebFPGA CLI v0.3

Connecting to remote synthesis engine...
200 {"status":"ok"} 

Attempting synthesis (saving to bitstream.bin)...
  - WF_blinky.v

... verbose output omitted ...

purging build directory...
synthesis complete!

$ webfpga flash bitstream.bin
ryan@mu2 ~/cli $ ./webfpga flash bitstream.bin 
WebFPGA CLI v0.3

Opening USB device...

Preparing device for flashing...
AT: Hi
API: C_WEBUSB+
APR: 000921
Found programmer.
Checking for FPGA module and its flash configuration...
APWE: wren
AMQ: SA016WHEe

Erasing device...
AMBE: DONE
AMQ: SA016WHEE

Flashing device...
AMW: OK
AMWD: 0  3e  0  3e
RESPONSE => 62 
```

## IceStorm Example.
If you would like to produce logic with Yosys, IceStorm, and friends
&mdash; then please check out
[webfpga_icestorm_examples](https://github.com/webfpga/webfpga_icestorm_examples).
Once you have produced a bitstream, simply run `webfpga flash bitstream.bin`.

## What is a compressed bitstream?

FPGA bitstreams are typically full of contiguous zeroes. Therefore,
compression on the host and decompression in the device's firmware
makes perfect sense. Flashing speeds are about 20x faster when using
compressed bitstreams.

Right now, the device's firmware expects compressed bitstreams. WebFPGA
doesn't support uncompressed, raw bitstreams (such as ones outputted
from iCECube/IceStorm tools.) These compressed bitstreams are chunked
into sub-64-byte chunks that fit into standard USB control transfer frames.

But don't fret! Our flashing utility automatically detects uncompressed
bitstreams and transparently compresses them before transferring them.
Bitstreams that originate from the official WebFPGA backend arrive
pre-compressed.
