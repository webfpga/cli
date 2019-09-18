# webfpga/cli
[![PyPI version](https://badge.fury.io/py/webfpga.svg)](https://badge.fury.io/py/webfpga)

Welcome to the official command-line utility for WebFPGA compatible devices.
If you are unfamiliar with WebFPGA, please checkout the homepage
([webfpga.io](https://webfpga.io)) or our Kickstarter
([webfpga.io/kickstarter](https://webfpga.io/kickstarter)).

This utility provides access to the official backend for Verilog synthesis.
It also provides flashing capability for the official WebFPGA family of
boards ([store.webfpga.io](https://store.webfpga.io)). You are free to use
bitstreams sourced from our tools, Lattice's iCECube, or IceStorm. They
will all work.

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

## 

## What is a compressed bitstream?

FPGA bitstreams are typically full of contiguous zeroes. Therefore,
compression on the host and decompression in the device's firmware
makes perfect sense. Flashing speeds are about 20x faster when using
compressed bitstreams.

Right now, the device's firmware expects compressed bitstreams. WebFPGA
doesn't support uncompressed, raw bitstreams (such as ones outputted
from iCECube/IceStorm tools.) These compressed bitstreams are blocked
into sub-64-byte chunks that fit into standard USB control transfer frames.

But don't fret! Our flashing utility automatically detects uncompressed
bitstreams and transparently compresses them before transferring them.
Bitstreams that originate from the official WebFPGA backend arrive
pre-compressed.
