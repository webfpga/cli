#!/usr/bin/env python3

import sys
import datetime
from sys import argv

# Compression and blocking constants
MAX_REC_SIZE = 63
MAX_BLK_SIZE = 64
MAX_ZEROS    = 127

# Returns true if the binary bitstream is already
# in the compressed format. If the binary buffer starts
# with 0xFF00, then it's definitely uncompressed.
def is_compressed(input_bytes):
    return (input_bytes[0] != 0xFF and input_bytes[1] != 0x00)

# Compresses the input bitstream if it isn't compressed already
# (If it's already compressed, it just returns the same bytes.)
def compress(input_bytes):
    if is_compressed(input_bytes):
        return input_bytes

    # Open input file and load into array
    print("Reading input bitstream...")
    bitstream = input_bytes
    print(f"Read {len(bitstream)} bytes.\n")

    # (0xFF signifies the start/end of the header)
    data_segment = []
    data_segment = [0xFF, 0x00 ] 
    data_segment.extend("E+".encode('utf-8'))

    x = datetime.datetime.now()
    print (f"date: {x}")

    data_segment.extend(x.strftime("%c").encode('utf-8'))
    data_segment.extend("+shastaplus".encode('utf-8'))
    data_segment.append(0x00)
    data_segment.append(0xFF)

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
    data_segment.extend(bitstream[index:])

    #######################################################################
    # compress
    #
    # Compressed data is stored in records. The first byte in a record is the
    # length. If the byte is 127 or less, then the following LEN-1 bytes are
    # non zero values of the data stream. If the byte is 128 or larger, (MSBit is set)
    # then the LEN masked with 0x7f is the number of zeros to be decompressed.
    # Records are repeated until EOF. Record maximum size can be set with
    # MAX_REC_SIZE. For WebFPGA, it is set to 63.

    index        = 0
    zero_count   = 0
    rec_number   = 0

    rec_buffer      = []
    compress_buffer = []

    rec_buffer.append(127)  # placeholder for length

    if data_segment[index] != 0:   # start zero flag with correct value
        zeros_flag = False
    else:
        zeros_flag = True
        
          
    while True:
        # once we hit a zero while collecting non-zeros, we flush record and switch to zero collecting
        if data_segment[index] == 0 and not zeros_flag:
            zeros_flag = True
            rec_buffer[0] = len(rec_buffer)  #len record
            #print(f"Compress A: Record is non zero, {index} {rec_number}#, len {len(rec_buffer)}.\n")
            rec_number += 1
            compress_buffer.extend(rec_buffer)   
            zero_count = 1   # we found a zero, so count
        else:
            if data_segment[index] != 0:       #check for zero
                if zeros_flag:                 # not a zero, but were counting zeros
                    zeros_flag = False
                    #print(f"Compress B: Record is zero, {index} {rec_number}#, #zeros {zero_count}.\n")
                    rec_number += 1
                    compress_buffer.append (128+zero_count) #set zero flag in MSBit
                    rec_buffer = []                # create new record of non zeros
                    rec_buffer.append(127)         # placehold for Length
                    
                rec_buffer.append(data_segment[index])
                # since we are counting non-zeros, check if max'ed bufer size
                if len(rec_buffer) == MAX_REC_SIZE-1:   # flush buffer if full
                    #print(f"Compress C: Record is non-zero, {index} {rec_number}#, len {len(rec_buffer)}.\n")
                    rec_number += 1
                    rec_buffer[0] = len(rec_buffer)     # set len of non zeros
                    compress_buffer.extend(rec_buffer)

                    rec_buffer = []          # create new record of non zeros
                    rec_buffer.append(127)   # placehold for Length
            else:                            # we got a zero
                if zero_count == MAX_ZEROS:
                    # flush zero count to output data stream
                    #print(f"Compress D: Record is zero, {index} {rec_number}#, #zeros {zero_count}.\n")
                    rec_number += 1
                    compress_buffer.append(128+zero_count)
                    zero_count = 1
                else:
                    zero_count += 1
                    
        index += 1
        if  index >= len(data_segment):
          break

    # now flush any remaining data in the buffer or zero counts
    if zeros_flag:
        print(f"Compress E: Final subrecord is zero rec# {rec_number}, #zeros {zero_count}.")
        rec_number += 1
        compress_buffer.append(128+zero_count)
    else:
        rec_buffer[0] = len(rec_buffer)
        print(f"Compress F: Final subrecord is non zero rec# {rec_number}, len {len(rec_buffer)}.")
        rec_number += 1
        compress_buffer.extend(rec_buffer)

    print("Compress G: Compressed file len: %6d, compression ratio %2.1f:1" % (len(compress_buffer),1/(len(compress_buffer)/len(bitstream))))

    print(f"Returning compressed bitstream...");
    return block(compress_buffer)

def block(compress_buffer):
    decompress_buffer = []
    index      = 0
    rec_number = 0

    while True:
        if compress_buffer[index] > 128:  #decompress zeros
            clen = compress_buffer[index] & 0x7f
            #print(f"Decompress A: Record is zero, {index} rec# {rec_number}#, #zeros {clen}.\n")
            for i in range(clen):
                decompress_buffer.append(0x0)
            index += 1
            rec_number += 1
        else:
            clen = compress_buffer[index] -1
            #print(f"Decompress B: Record is non-zero, {index} rec# {rec_number}#, len {clen}.\n")
            for i in range(clen):
                decompress_buffer.append(compress_buffer[i+index+1])
            index += clen + 1
            rec_number += 1

        if index >= len(compress_buffer):
            break
              
    print(f"Decompress B: number of records decompressed {rec_number} length {len(decompress_buffer)}.")
    print (f"decompressed: {decompress_buffer} \n")

    #######################################################################
    # blocking
    #
    # blocking is putting a group of records into a block.
    # This is done to help make transfers to the de-compressor code in
    # a MCU very easy to handle. For WebUSB we use 64 bytes for the block size. 
    # Each block contains complete records.
    # The first byte of a block is the block length, followed
    # by complete record(s), until max block size is reached.
    # No partial records are allowed.
    # Last block is marked with its length's byte MSBit set.

    index        = 0
    block_index  = 1

    block_buffer = []
    blocks_buffer= []

    block_number = 0
    record_number= 0

    block_buffer.append(127)  # placeholder for length

    while True:
        if compress_buffer[index] > 128:   # zero record
            #print(f"Blocks A: zero record {index} #{record_number}, # of zeros {compress_buffer[index]-128}.\n")
            if block_index == MAX_BLK_SIZE:
                #print(f"Blocks B: flush case, blk# {block_number} then move zero record to block buffer.\n")
                block_buffer[0] = block_index      # put block len at start of block
                block_number += 1
                blocks_buffer.extend(block_buffer)
                #print(f"Blocks B1: {block_buffer}\n")
                block_buffer = []
                block_buffer.append(127)  # placeholder for length
                block_index = 1
                block_buffer.append(compress_buffer[index]) 
                block_index += 1
            else:
                block_buffer.append(compress_buffer[index])
                block_index += 1
            index += 1
        else:       # non zero record
            #print(f"Blocks C: nonzero record {index} #{record_number}, len {compress_buffer[index]}.\n")
            if block_index + (compress_buffer[index]) >= MAX_BLK_SIZE+1:
                #print(f"Blocks D: flush first and start new block.\n")
                block_buffer[0] = block_index      # put block len at start of block
                block_index = 1
                block_number += 1
                blocks_buffer.extend(block_buffer)
                #print(f"Blocks D1: {block_buffer}\n")
                block_buffer = []
                block_buffer.append(127)  # placeholder for length

                # move current record to block buffer
                #print(f"Blocks E: flush case, blk# {block_number} then move non-zero record to block buffer.\n")
                for i in range(compress_buffer[index]):       # of non-zero transfers
                    block_buffer.append(compress_buffer[i+index])
                block_index += compress_buffer[index]
                #print(f"Blocks E1: {block_buffer}\n")

            else:      # move non-zero record to block buffer
                #print(f"Blocks F: Non-flush case, just move non-zero record to block buffer.\n")
                for i in range(compress_buffer[index]):       # of non-zero transfers
                    block_buffer.append(compress_buffer[i+index])
                block_index += compress_buffer[index]

            index = index + compress_buffer[index]
                
        
        record_number += 1
        if index >= len(compress_buffer):
            break

    print(f"Blocks G: Last block, flush it case.")
    block_buffer[0] = block_index + 128  # set last block flag with length
    blocks_buffer.extend(block_buffer)

    print(f"Blocks: Blocks {block_number+1}, records {record_number}.")
    #print (f"blocking: {blocks_buffer} \n")

    print(f"Returning blocks bitstream\n")
    return bytes(blocks_buffer)
