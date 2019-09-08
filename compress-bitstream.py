#!/usr/bin/env python

import sys
from sys import argv

# Parse arguments
if len(argv) != 2 or "--help" in argv or "-h" in argv:
    print(f"usage: {argv[0]} <input.bin>")
    print("WebFPGA Bitstream Compression Utility")
    exit(1)
input_filename  = argv[1]
#output_filename = argv[1] + ".cbin"
output_filename = "output.cbin"

# Print banner
print("----------------------------------------")
print("WebFPGA Bitstream Compression Utility\n")
print("Input: ",  input_filename)
print("Output:", output_filename)
print("----------------------------------------\n")

# Open input file and load into array
print("Reading input bitstream...")
f = open(input_filename, "rb")
bitstream = bytearray(f.read())
print(f"Read {len(bitstream)} bytes.\n")

# Initialize the output array to hold the compressed bitstream
# (0xFF signifies the start/end of the header)
output = [0xFF, 0x12, 0x34, 0xFF] # (placeholder header for now...)

# Locate the start of actual data in the input bitstream
assert bitstream[0] == 0xFF, "first byte of input bitstream != 0xFF"
print("Searching start of input bitstream data segment...")
for index in range(len(bitstream)):
    # 0xFF marks the end of the input bitstream's header
    print(f"Byte {index}: {bitstream[index]}")
    if bitstream[index] == 0xFF and index != 0:
        index += 1
        break
print(f"Found data segment start at byte {index}.\n");
data_segment = bitstream[index:]

# Compress blocks
# TODO
for x in data_segment:
    continue

# Save file
print(f"Saving compressed bitstream ({output_filename})...")
with open(output_filename, "wb") as f:
    f.write(bytes(output))
