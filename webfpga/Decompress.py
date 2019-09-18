def decompress(block_buffer):
    #######################################################################
    # de-blocking with decompression
    #

    index            = 0
    deblock_buffer   = []
    record_number    = 0
    last_block       = False

    while True:        # loop every block
        last_block = ((blocks_buffer[index] & 0x80) == 0x80)
        block_bytes = blocks_buffer[index] & 0x7f
        index += 1

        while True:     # loop thur records in a block
            record_len = blocks_buffer[index]  & 0x7f
            if blocks_buffer[index] > 128:  #decompress zeros
                #print(f"Decompress A: Record is zero, {index} rec# {record_number}#, #zeros {record_len}.\n")
                for i in range(record_len):
                    deblock_buffer.append(0x0)
                index         += 1
                block_bytes   -= 1
                record_number += 1
            else:
                #print(f"Decompress B: Record is non-zero, {index} rec# {record_number}#, len {record_len}.\n")
                for i in range(record_len-1):
                    deblock_buffer.append(blocks_buffer[i+index+1])
                index         += record_len 
                block_bytes   -= record_len
                record_number += 1

            #print (f"deblock {deblock_buffer}\n")
            if block_bytes == 1:
                break

        if last_block:
            break

    print(f"De-blocking: records {record_number}, file length {len(deblock_buffer)}.")
    #print (f"De-blocking: {deblock_buffer} \n")

    print(f"Returning deblocked bitstream")
    return bytes(deblock_buffer)
