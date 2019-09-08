#!/usr/bin/env python

from sys import argv

# Parse arguments
if len(argv) != 2 or "--help" in argv or "-h" in argv:
    print(f"usage: {argv[0]} <input.bin>")
    print("WebFPGA Bitstream Compression Utility")
    exit(1)
input_filename  = argv[1]
output_filename = argv[2] + ".cbin"

# Print banner
print("----------------------------------------")
print("WebFPGA Bitstream Compression Utility\n")
print("Input: ",  input_filename)
print("Output:", output_filename)
print("----------------------------------------\n")

# Open input file and load into array
print("Reading input bitstream...")
f = open(input_filename, "rb")
input  = f.read()
output = []
print(f"Read {len(input)} bytes.\n")

# Substitute header
for x in input:
    print(x)

# Compress blocks
# TODO

# Save file
# TODO
