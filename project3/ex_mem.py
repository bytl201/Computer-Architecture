class ExMem():
    def __init__(self):
        # alu operation result 
        self.alu_result = None

        # register dest
        self.dest = None

        # sb value
        self.sb_value = None

        # control signals
        self.mem_read = None
        self.mem_write = None
        self.mem_to_reg = None
        self.reg_write = None

    def set(self, mem_read: int, mem_write: int, mem_to_reg: int | None, reg_write: int, alu_result: int, sb_value: int | None, dest: int | None):
        # alu operation result
        self.alu_result = alu_result

        # rt or rd
        self.dest = dest

        # sb value
        self.sb_value = sb_value
        
        # control signals
        self.mem_read = mem_read
        self.mem_write = mem_write
        self.mem_to_reg = mem_to_reg
        self.reg_write = reg_write

    def get(self):
        return [self.mem_read, self.mem_write, self.mem_to_reg, self.reg_write, self.alu_result, self.sb_value, self.dest]