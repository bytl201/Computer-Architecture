class IdEx:

    def __init__(self):
        # instruction
        self.rs = None
        self.rt = None
        self.rd = None
        self.offset = None
        self.opcode = None
        self.funct = None

        # default control signals
        self.reg_dst = None
        self.alu_src = None
        self.mem_to_reg = None
        self.reg_write = None
        self.mem_read = None
        self.mem_write = None
        self.alu_op = None

    def reset(self):
        # instruction
        self.rs = None
        self.rt = None
        self.rd = None
        self.offset = None
        self.opcode = None
        self.funct = None
    
        # default control signals
        self.reg_dst = None
        self.alu_src = None
        self.mem_to_reg = None
        self.reg_write = None
        self.mem_read = None
        self.mem_write = None
        self.alu_op = None

    def set(self, rs, rt, opcode, funct: int | None, rd: int | None, offset: int | None):
        # reset the values
        self.reset()

        # instructions
        self.rs = rs
        self.rt = rt
        self.rd = rd
        self.offset = offset
        self.opcode = opcode
        self.funct = funct

        # add and subtract
        if opcode == 0 and (funct == 0x20 or funct == 0x22):
            self.reg_dst = 1
            self.alu_src = 0
            self.mem_to_reg = 0
            self.reg_write = 1
            self.mem_read = 0
            self.mem_write = 0
            self.alu_op = 0b10

        # lb
        elif opcode == 0x20:
            self.reg_dst = 0
            self.alu_src = 1
            self.mem_to_reg = 1
            self.reg_write = 1
            self.mem_read = 1
            self.mem_write = 0
            self.alu_op = 0b00

        # sb
        elif opcode  == 0x28:
            self.alu_src = 1
            self.reg_write = 0
            self.mem_read = 0
            self.mem_write = 1
            self.alu_op = 0b00

    def get(self):
        return [self.rs, self.rt, self.opcode, self.funct, self.rd, self.offset]