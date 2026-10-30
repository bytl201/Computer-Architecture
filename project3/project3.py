from ex_mem import ExMem
from id_ex import IdEx
from if_id import IfId
from mem_wb import MemWb

def if_stage(instruction: int, ifid_write: IfId):
    # write the new instruction to the if/id reg
    ifid_write.set(instruction)

def id_stage(ifid_read: IfId, idex_write: IdEx, regs: list[int]):
    # read the instruction from ifid_read obj
    instruction = ifid_read.instruction

    # NOP
    if instruction is None or instruction == 0x0:
        idex_write.set(None, 0, None, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        return

    # mask for each field in instruction format
    opcode_mask = 0b11111100000000000000000000000000
    rs_mask = 0b00000011111000000000000000000000
    rt_mask = 0b00000000000111110000000000000000
    rd_mask = 0b00000000000000001111100000000000
    funct_mask = 0b00000000000000000000000000111111
    offset_mask = 0b00000000000000001111111111111111

    # get value after mask and shift
    opcode = (instruction & opcode_mask) >> 26
    rs = (instruction & rs_mask) >> 21
    rt = (instruction & rt_mask) >> 16
    rd = (instruction & rd_mask) >> 11
    funct = instruction & funct_mask
    offset = instruction & offset_mask
    reg_20_16 = rt
    reg_15_11 = rd
    
    # check if offset value is bigger than or equal to 2^15 and then subtract 2^16 to get signed value. 
    if offset >= 0x8000:
        offset = offset - 0x10000

    # get values from the register
    rs_val = regs[rs]
    rt_val = regs[rt]

    # R-format
    if opcode == 0 and (funct == 0x20 or funct == 0x22):
        # set control signals
        reg_dst = 1
        alu_src = 0
        mem_to_reg = 0
        reg_write = 1
        mem_read = 0
        mem_write = 0
        alu_op = 0b10

        idex_write.set(reg_dst, alu_src, mem_to_reg, reg_write, mem_read, mem_write, alu_op, opcode, rs_val, rt_val, reg_20_16, reg_15_11, offset, funct)

    # lb opcode (mem -> reg)
    elif opcode == 0x20:
        reg_dst = 0
        alu_src = 1
        mem_to_reg = 1
        reg_write = 1
        mem_read = 1
        mem_write = 0
        alu_op = 0b00

        idex_write.set(reg_dst, alu_src, mem_to_reg, reg_write, mem_read, mem_write, alu_op, opcode, rs_val, rt_val, reg_20_16, reg_15_11, offset, funct)
    
    # sb opcode (reg -> mem)
    elif opcode == 0x28:
        reg_dst = None
        alu_src = 1
        mem_to_reg = None
        reg_write = 0
        mem_read = 0
        mem_write = 1
        alu_op = 0b00

        idex_write.set(reg_dst, alu_src, mem_to_reg, reg_write, mem_read, mem_write, alu_op, opcode, rs_val, rt_val, reg_20_16, reg_15_11, offset, funct)
        
def ex_stage(idex_read: IdEx, exmem_write: ExMem):
    # instructions
    opcode = idex_read.opcode
    rs = idex_read.rs
    rt = idex_read.rt
    funct = idex_read.funct
    offset = idex_read.offset
    reg_20_16 = idex_read.reg_20_16
    reg_15_11 = idex_read.reg_15_11

    # set control signals
    reg_dst = idex_read.reg_dst
    alu_src = idex_read.alu_src
    mem_to_reg = idex_read.mem_to_reg
    reg_write = idex_read.reg_write
    mem_read = idex_read.mem_read
    mem_write = idex_read.mem_write
    alu_op = idex_read.alu_op

    # NOP (contridicting control signals) or clock cycles not ran yet
    if (reg_dst is None and alu_src == 0 and mem_to_reg is None) or (reg_dst is None and alu_src is None and mem_to_reg is None):
        exmem_write.set(0, 0, None, 0, 0, None, None)

    # R-format
    elif idex_read.alu_src == 0 and idex_read.alu_op == 0b10 and idex_read.reg_dst == 1:
        # add
        if funct == 0x20:
            value = rs + rt 
            exmem_write.set(mem_read, mem_write, mem_to_reg, reg_write, value, None, reg_15_11) 

        # subtract
        elif funct == 0x22:
            value = rs - rt 
            exmem_write.set(mem_read, mem_write, mem_to_reg, reg_write, value, None, reg_15_11) 
    # lb 
    elif alu_src == 1 and alu_op == 0b00 and reg_dst == 0:
        value = rs + offset 
        exmem_write.set(mem_read, mem_write, mem_to_reg, reg_write, value, None, reg_20_16) 

    # sb
    elif alu_src == 1 and alu_op == 0b00 and reg_dst is None:
        value = rs + offset 
        exmem_write.set(mem_read, mem_write, mem_to_reg, reg_write, value, rt, None) 

def mem_stage(exmem_read: ExMem, memwb_write: MemWb, main_mem: list[int]):
    # control signal
    mem_read = exmem_read.mem_read
    mem_write = exmem_read.mem_write
    mem_to_reg = exmem_read.mem_to_reg
    reg_write = exmem_read.reg_write

    # alu result, destination register, sb value
    alu_result = exmem_read.alu_result
    dest = exmem_read.dest
    sb_value = exmem_read.sb_value

    # NOP (contridicting control signals) or clock cycles not ran yet
    if (alu_result is None and dest is None) or (mem_read == 0 and mem_write == 0 and alu_result == 0 and dest == None):
        memwb_write.set(None, 0, None, None, None)

    # R-format
    elif mem_read == 0 and mem_write == 0 and mem_to_reg == 0 and reg_write == 1:
        memwb_write.set(mem_to_reg, reg_write, alu_result, None, dest)

    # lb (load byte) mem -> reg
    elif mem_read == 1 and mem_write == 0 and mem_to_reg == 1 and reg_write == 1:
        lb_data = main_mem[alu_result]  
        memwb_write.set(mem_to_reg, reg_write, None, lb_data, dest)

    # sb (store byte)
    elif mem_read == 0 and mem_write == 1 and mem_to_reg is None and reg_write == 0:
        main_mem[alu_result] = (sb_value % 0x100) 
        memwb_write.set(mem_to_reg, reg_write, None, None, None)

def wb_stage(memwb_read: MemWb, regs: list[int]):
    # values
    alu_result = memwb_read.alu_result
    lb_data = memwb_read.lb_data
    dest = memwb_read.dest

    # control signals
    mem_to_reg = memwb_read.mem_to_reg
    reg_write = memwb_read.reg_write

    # write to register using alu result
    if mem_to_reg == 0 and reg_write == 1:
        regs[dest] = alu_result  
    # write to resgister using lb_data
    elif mem_to_reg == 1 and reg_write == 1:
        regs[dest] = lb_data 

def copy_write_to_read(
    write: IfId | IdEx | ExMem | MemWb,
    read: IfId | IdEx | ExMem | MemWb
):
    # if -> id
    if isinstance(write, IfId):
        read.set(write.get()) 

    # id -> ex
    elif isinstance(write, IdEx):
        read.set(*write.get())

    # ex -> mem
    elif isinstance(write, ExMem):
        read.set(*write.get())

    # mem -> wb
    elif isinstance(write, MemWb):
        read.set(*write.get())

def print_out_everything(index: int, ifid_write: IfId, ifid_read: IfId,
                         idex_write: IdEx, idex_read: IdEx,
                         exmem_write: ExMem, exmem_read: ExMem,
                         memwb_write: MemWb, memwb_read: MemWb,
                         regs: list[int], file):

    file.write(f"Clock Cycle {index}\n\n")

    # TODO: IF/ID
    # write
    file.write(f"**IF/ID Write (written to by the IF stage)**\n")
    instruction = f"{ifid_write.instruction:08X}" if ifid_write.instruction else f"{0:08X}"
    file.write(f"Instruction = 0x{instruction}\n")

    # read
    file.write(f"**IF/ID Read (read by the ID stage)**\n")
    instruction = f"{ifid_read.instruction:08X}" if ifid_read.instruction else f"{0:08X}"
    file.write(f"Instruction = 0x{instruction}\n\n")


    # TODO: ID/EX
    # write
    file.write(f"**ID/EX Write (written to by the ID stage)**\n")

    rs = idex_write.rs
    rt = idex_write.rt
    offset = idex_write.offset
    funct = idex_write.funct
    reg_20_16 = idex_write.reg_20_16
    reg_15_11 = idex_write.reg_15_11

    reg_dst = idex_write.reg_dst
    alu_src = idex_write.alu_src
    mem_to_reg = idex_write.mem_to_reg
    reg_write = idex_write.reg_write
    mem_read = idex_write.mem_read
    mem_write = idex_write.mem_write
    alu_op = idex_write.alu_op

    if (reg_dst is None and alu_src == 0 and mem_to_reg is None) or (reg_dst is None and alu_src is None and mem_to_reg is None):
        file.write(f"Control = {0:08X}\n")

    else:
        # R-format
        if reg_dst == 1 and alu_src == 0 and alu_op == 0b10:
            offset = "X"

        # lb
        elif reg_dst == 0 and alu_src == 1 and mem_read == 1:
            funct = "X"

        # sb
        elif reg_dst is None and alu_src == 1 and mem_write == 1:
            funct = "X"

        # don't-care control signals
        if reg_dst is None:
            reg_dst = "X"

        if mem_to_reg is None:
            mem_to_reg = "X"

        file.write(
            f"Control: RegDst = {reg_dst}, ALUSrc = {alu_src}, ALUOp = {alu_op}, MemRead = {mem_read}, MemWrite = {mem_write}, MemToReg = {mem_to_reg}, RegWrite = {reg_write}\n"
            f"         Register 1 Value = {rs}, Register 2 Value = {rt}, Offset = {offset}, Register 20-16 = {reg_20_16}, Register 15-11 = {reg_15_11}, Function = {funct}\n"
        )

    # read
    file.write(f"**ID/EX Read (read by the EX stage)**\n")

    rs = idex_read.rs
    rt = idex_read.rt
    offset = idex_read.offset
    funct = idex_read.funct
    reg_20_16 = idex_read.reg_20_16
    reg_15_11 = idex_read.reg_15_11

    reg_dst = idex_read.reg_dst
    alu_src = idex_read.alu_src
    mem_to_reg = idex_read.mem_to_reg
    reg_write = idex_read.reg_write
    mem_read = idex_read.mem_read
    mem_write = idex_read.mem_write
    alu_op = idex_read.alu_op

    if (reg_dst is None and alu_src == 0 and mem_to_reg is None) or (reg_dst is None and alu_src is None and mem_to_reg is None):
        file.write(f"Control = {0:08X}\n\n")

    else:
        # R-format
        if reg_dst == 1 and alu_src == 0 and alu_op == 0b10:
            offset = "X"

        # lb
        elif reg_dst == 0 and alu_src == 1 and mem_read == 1:
            funct = "X"

        # sb
        elif reg_dst is None and alu_src == 1 and mem_write == 1:
            funct = "X"

        # don't-care control signals
        if reg_dst is None:
            reg_dst = "X"

        if mem_to_reg is None:
            mem_to_reg = "X"

        file.write(
            f"Control: RegDst = {reg_dst}, ALUSrc = {alu_src}, ALUOp = {alu_op}, MemRead = {mem_read}, MemWrite = {mem_write}\n"
            f"         MemToReg = {mem_to_reg}, RegWrite = {reg_write}, Register 1 Value = {rs}, Register 2 Value = {rt}, Offset = {offset}, Register 20-16 = {reg_20_16}, Register 15-11 = {reg_15_11}, Function = {funct}\n\n"
        )

    # TODO: EX/MEM
    # write
    file.write(f"**EX/MEM Write (written to by the EX stage)**\n")

    alu_result = exmem_write.alu_result
    dest = exmem_write.dest
    sb_value = exmem_write.sb_value

    mem_read = exmem_write.mem_read
    mem_write = exmem_write.mem_write
    mem_to_reg = exmem_write.mem_to_reg
    reg_write = exmem_write.reg_write

    if (alu_result is None and dest is None) or (mem_read == 0 and mem_write == 0 and alu_result == 0 and dest is None):

        file.write(f"Control = {0:08X}\n")

    else:
        # sb
        if mem_write == 1:
            dest = "X"
            mem_to_reg = "X"

        # add, sub, or lb
        else:
            sb_value = "X"

        file.write(
            f"Control: MemRead = {mem_read}, MemWrite = {mem_write}, MemToReg = {mem_to_reg}, RegWrite = {reg_write}\n"
            f"         ALUResult = {alu_result}, SB Value = {sb_value}, Write Register Number = {dest}\n"
        )

    # read
    file.write(f"**EX/MEM Read (read by the MEM stage)**\n")

    alu_result = exmem_read.alu_result
    dest = exmem_read.dest
    sb_value = exmem_read.sb_value

    mem_read = exmem_read.mem_read
    mem_write = exmem_read.mem_write
    mem_to_reg = exmem_read.mem_to_reg
    reg_write = exmem_read.reg_write

    if (alu_result is None and dest is None) or (mem_read == 0 and mem_write == 0 and alu_result == 0 and dest is None):
        file.write(f"Control = {0:08X}\n\n")

    else:
        # sb
        if mem_write == 1:
            dest = "X"
            mem_to_reg = "X"

        # add, sub, or lb
        else:
            sb_value = "X"

        file.write(
            f"Control: MemRead = {mem_read}, MemWrite = {mem_write}, MemToReg = {mem_to_reg}, RegWrite = {reg_write}\n"
            f"         ALUResult = {alu_result}, SB Value = {sb_value}, Write Register Number = {dest}\n\n"
        )

    # TODO: MEM/WB
    # write
    file.write(f"**MEM/WB Write (written to by the MEM stage)**\n")

    alu_result = memwb_write.alu_result
    lb_data = memwb_write.lb_data
    dest = memwb_write.dest
    mem_to_reg = memwb_write.mem_to_reg
    reg_write = memwb_write.reg_write

    if (mem_to_reg == 0 and reg_write == 1) or (mem_to_reg == 1 and reg_write == 1):

        # R-format
        if mem_to_reg == 0:
            lb_data = "X"

        # lb
        elif mem_to_reg == 1:
            alu_result = "X"

        file.write(
            f"Control: MemToReg = {mem_to_reg}, RegWrite = {reg_write}, LB Value = {lb_data}, ALUResult = {alu_result}, Write Register Number = {dest}\n"
        )

    else:
        file.write(f"Control = {0:08X}\n")

    # read
    file.write(f"**MEM/WB Read (read by the WB stage)**\n")

    alu_result = memwb_read.alu_result
    lb_data = memwb_read.lb_data
    dest = memwb_read.dest
    mem_to_reg = memwb_read.mem_to_reg
    reg_write = memwb_read.reg_write

    if (mem_to_reg == 0 and reg_write == 1) or (mem_to_reg == 1 and reg_write == 1):

        # R-format
        if mem_to_reg == 0:
            lb_data = "X"

        # lb
        elif mem_to_reg == 1:
            alu_result = "X"

        file.write(
            f"Control: MemToReg = {mem_to_reg}, RegWrite = {reg_write}, LB Value = {lb_data}, ALUResult = {alu_result}, Write Register Number = {dest}\n\n"
        )

    else:
        file.write(f"Control = {0:08X}\n\n")


    # register
    file.write(f"**Register**\n")
    file.write("[")

    for i in regs:
        file.write(f"{i:08X} ")

    file.write("]\n\n")

def main():
    # main memory allocation
    main_mem = [(i % 0x100) for i in range(1024)]

    # registers
    regs = [i+0x100 if i != 0 else 0 for i in range(32)]

    # instructions
    instruction_cache = [0xa1020000, 0x810AFFFC, 0x00831820, 0x01263820, 
                         0x01224820, 0x81180000, 0x81510010, 0x00624022, 
                         0x00000000, 0x00000000, 0x00000000, 0x00000000]

    # if/id pipeline register
    ifid_write = IfId()
    ifid_read = IfId()

    # id/ex pipeline register
    idex_write = IdEx()
    idex_read = IdEx()

    # ex/mem pipeline register
    exmem_write = ExMem()
    exmem_read = ExMem()

    # mem/wb pipeline register
    memwb_write = MemWb()
    memwb_read = MemWb()

    # file to write output 
    with open("output.txt", "w") as file:
        # iterate over each instruction in instruction_cache
        for index in range(len(instruction_cache)):
            instruction = instruction_cache[index]

            # handle each pipeline stage
            if_stage(instruction, ifid_write)
            id_stage(ifid_read, idex_write, regs)
            ex_stage(idex_read, exmem_write)
            mem_stage(exmem_read, memwb_write, main_mem)
            wb_stage(memwb_read, regs)

            # print the values
            print_out_everything(index, ifid_write, ifid_read,
                                idex_write, idex_read,
                                exmem_write, exmem_read,
                                memwb_write, memwb_read, regs, file)

            # write -> read copy over values
            copy_write_to_read(ifid_write, ifid_read)
            copy_write_to_read(idex_write, idex_read)
            copy_write_to_read(exmem_write, exmem_read)
            copy_write_to_read(memwb_write, memwb_read)

if __name__ == "__main__":
    main()