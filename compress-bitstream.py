#!/usr/bin/env python

from sys import argv

# Parse arguments
if len(argv) != 3 or "--help" in argv or "-h" in argv:
    print(f"usage: {argv[0]} <input.bin> <output.cbin>")
    print("WebFPGA Bitstream Compression Utility")
    exit(1)
input_filename  = argv[1]
output_filename = argv[2]

print("----------------------------------------")
print("WebFPGA Bitstream Compression Utility\n")
print("Input: ",  input_filename)
print("Output:", output_filename)
print("----------------------------------------\n")

f = open(input_filename, "rb")
f.read()
