from cache import CacheSlot

def main():
    # initialization
    main_memory = []

    for i in range(2048):
        data = i % 256
        main_memory.append(data)

    cache = [CacheSlot() for _ in range(16)]


    # masks
    block_offset_mask = 0xF
    index_mask = 0xF0
    tag_mask = 0x700
                    
    while True:
        option = input("(R)ead, (W)rite, or (D)isplay Cache?\n").lower()

        match option:
            case "r":
                address = int(input("What address would you like read?\n"), 16)

                # distect the data
                block_offset = address & block_offset_mask
                index = (address & index_mask) >> 4 
                tag = (address & tag_mask) >> 8 
                
                # get the CacheSlot object
                slot = cache[index]

                # call the read func
                slot.read(tag, index, block_offset, address, main_memory)
            case "w":
                # input
                address = int(input("What address would you like to write to?\n"), 16)
                data = int(input("What data would you like to write at that address?\n"), 16)

                # distect the data
                block_offset = address & block_offset_mask
                index = (address & index_mask) >> 4 
                tag = (address & tag_mask) >> 8 

                # get the CacheSlot object
                slot = cache[index]

                # call the write func
                slot.write(data, tag, index, block_offset, address, main_memory)
            case "d":
                print("Slot Valid Dirty Tag     Data")

                # iterate over each CacheSlot in arry
                for i in range(len(cache)):
                    cache_slot = cache[i]
                    print(f"{i:X}    {cache_slot.valid_bit}     {cache_slot.dirty_bit}     {cache_slot.tag:X}       ", end="")

                    # iterate over each element in CacheSlot's block
                    for i in range(16):
                        print(f"{cache_slot.block[i]:02X}   ", end="")

                    print()


if __name__ == "__main__":
    main()