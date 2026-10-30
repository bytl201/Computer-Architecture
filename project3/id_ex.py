class IdEx:

    def __init__(self):
        # instruction
        self.rs = None
        self.rt = None
        self.offset = None
        self.opcode = None
        self.funct = None
        self.reg_20_16 = None
        self.reg_15_11 = None

        # default control signals
        self.reg_dst = None
        self.alu_src = None
        self.mem_to_reg = None
        self.reg_write = None
        self.mem_read = None
        self.mem_write = None
        self.alu_op = None

    def set(self, reg_dst: int | None, alu_src: int, mem_to_reg: int | None, reg_write: int, mem_read: int, mem_write: int, alu_op: int,
            opcode: int, rs: int, rt: int, reg_20_16: int, reg_15_11: int, offset: int, funct: int):

        # instructions
        self.opcode = opcode
        self.rs = rs
        self.rt = rt
        self.funct = funct
        self.offset = offset
        self.reg_20_16 = reg_20_16
        self.reg_15_11 = reg_15_11

        # control signals
        self.reg_dst = reg_dst
        self.alu_src = alu_src
        self.mem_to_reg = mem_to_reg
        self.reg_write = reg_write
        self.mem_read = mem_read
        self.mem_write = mem_write
        self.alu_op = alu_op

    def get(self):
        return [self.reg_dst, self.alu_src, self.mem_to_reg, self.reg_write, self.mem_read, self.mem_write, self.alu_op ,
            self.opcode, self.rs, self.rt, self.reg_20_16, self.reg_15_11, self.offset, self.funct]