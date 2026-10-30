class MemWb():
    def __init__(self):
        # alu result
        self.alu_result = None

        # data from memory
        self.lb_data = None

        # register dest
        self.dest = None

        # control signal
        self.mem_to_reg = None
        self.reg_write = None

    def set(self, mem_to_reg: int | None, reg_write: int, alu_result: int | None, lb_data: int | None, dest: int | None):
        # alu result
        self.alu_result = alu_result
    
        # data from memory
        self.lb_data = lb_data
    
        # rt or rd
        self.dest = dest
    
        # control signal
        self.mem_to_reg = mem_to_reg
        self.reg_write = reg_write

    def get(self):
        return [self.mem_to_reg, self.reg_write, self.alu_result, self.lb_data, self.dest]