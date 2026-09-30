class CacheSlot:
    def __init__(self):
        self.valid_bit = 0
        self.dirty_bit = 0
        self.tag = 0
        self.block = [0] * 16

    def read_main_memory_block(self, address: int, main_memory: list, tag: int):
        # get the start of the block address
        start_address = address & 0x7F0
            
        # start transfering data from main memory to cache block
        for i in range(16):
            self.block[i] = main_memory[start_address+i]
            
        # update the tag and valid bit
        self.valid_bit = 1
        self.tag = tag

    def write_main_memory(self, index: int, main_memory: list):
        # reconstruct the address
        index = index << 4
        start_address = (self.tag << 8) + index 

        # start transfering from cache to main memory
        for i in range(16):
            main_memory[start_address+i] = self.block[i]

    def read(self, tag: int, index: int, block_offset: int, address: int, main_memory: list):
        
        # cache hit
        if self.valid_bit == 1 and self.tag == tag:
            print(f"At address {address:X}, there is the value: {self.block[block_offset]:X} (Cache Hit)\n")
            
        # cache miss
        else:
            if self.dirty_bit == 1:
                self.write_main_memory(index, main_memory)
                self.dirty_bit = 0

            self.read_main_memory_block(address, main_memory, tag)

            print(f"At address {address:X}, there is the value: {self.block[block_offset]:X} (Cache Miss)\n")

    def write(self, data: int, tag: int, index: int, block_offset: int, address: int, main_memory: list):
        # cache hit
        if self.valid_bit == 1 and self.tag == tag :
            # update the dirty_bit
            self.dirty_bit = 1

            # write the data to block
            self.block[block_offset] = data

            print(f"Value {data:X} has been written to address {address:X}. (Cache Hit)\n")

        # cache miss
        else:
            # dirty block
            if self.dirty_bit == 1:
            
                self.write_main_memory(index, main_memory)

            # nothing in the cache
            self.read_main_memory_block(address, main_memory, tag)
            self.dirty_bit = 1
            self.block[block_offset] = data
            self.tag = tag

            print(f"Value {data:X} has been written to address {address:X}. (Cache Miss)\n")