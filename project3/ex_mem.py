class ExMem():
    def __init__(self):
        # alu operation result 
        self.value = None

        # rt or rd
        self.dest = None

        # control signals
        self.mem_write = None
        self.mem_to_reg = None
        self.mem_read = None

    def reset(self):
        # alu operation result
        self.value = None
        
        # rt or rd
        self.dest = None

        # control signals
        self.mem_write = None
        self.mem_to_reg = None
        self.mem_read = None

    def set(self, value: int | None, dest: int | None, mem_write: int | None, mem_to_reg: int | None, mem_read: int | None):
        # reset values
        self.reset()
        
        # alu operation result
        self.value = value

        # rt or rd
        self.dest = dest
        
        # control signals
        self.mem_write = mem_write
        self.mem_read = mem_read
        self.mem_to_reg = mem_to_reg

    def get(self):
        return [self.value, self.dest, self.mem_write, self.mem_to_reg, self.mem_read]