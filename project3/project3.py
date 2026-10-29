from ex_mem import ExMem
from id_ex import IdEx
from if_id import IfId
from mem_wb import MemWb

RESET = "\033[0m"
RED_BG = "\033[41m"

def if_stage(instruction: int, ifid_write: IfId):
    # write the new instruction to the if/id reg
    ifid_write.set(instruction)

def id_stage(ifid_read: IfId, idex_write: IdEx, regs: list[int]):
    # read the instruction from ifid_read obj
    instruction = ifid_read.instruction

    # NOP
    if instruction is None or instruction == 0x0:
        idex_write.set(0,0,0,0,0,0)
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

        idex_write.set(reg_dst, alu_src, mem_to_reg, reg_write, mem_read, mem_write, alu_op, opcode, rs_val, rt_val, rd, offset, funct)

    # lb opcode (mem -> reg)
    elif opcode == 0x20:
        reg_dst = 0
        alu_src = 1
        mem_to_reg = 1
        reg_write = 1
        mem_read = 1
        mem_write = 0
        alu_op = 0b00

        idex_write.set(reg_dst, alu_src, mem_to_reg, reg_write, mem_read, mem_write, alu_op, opcode, rs_val, rt, rd, offset, funct)
    
    # sb opcode (reg -> mem)
    elif opcode == 0x28:
        reg_dst = None
        alu_src = 1
        mem_to_reg = None
        reg_write = 0
        mem_read = 0
        mem_write = 1
        alu_op = 0b00

        idex_write.set(reg_dst, alu_src, mem_to_reg, reg_write, mem_read, mem_write, alu_op, opcode, rs_val, rt_val, rd, offset, funct)
        
def ex_stage(idex_read: IdEx, exmem_write: ExMem):

    # R-format
    if idex_read.alu_src == 0 and idex_read.alu_op == 0b10 and idex_read.reg_dst == 1:
        funct = idex_read.funct
        rd = idex_read.rd

        # add
        if funct == 0x20:
            value = idex_read.rs + idex_read.rt # type: ignore
            exmem_write.set(value, rd, idex_read.mem_write, idex_read.mem_to_reg, idex_read.mem_read)
        # sub
        elif funct == 0x22:
            value = idex_read.rs - idex_read.rt # type: ignore
            exmem_write.set(value, rd, idex_read.mem_write, idex_read.mem_to_reg, idex_read.mem_read)

    # NOP
    elif idex_read.alu_src is None and idex_read.alu_op is None and idex_read.reg_dst is None:
            value = None
            exmem_write.set(value, idex_read.rd, idex_read.mem_write, idex_read.mem_to_reg, idex_read.mem_read)

    # I-format
    else:
        value = idex_read.rs + idex_read.offset # type: ignore
        exmem_write.set(value, idex_read.rt, idex_read.mem_write, idex_read.mem_to_reg, idex_read.mem_read)

def mem_stage(exmem_read: ExMem, memwb_write: MemWb, main_mem: list[int]):
    # control signal
    mem_write, mem_read, mem_to_reg = exmem_read.mem_write, exmem_read.mem_read, exmem_read.mem_to_reg

    # alu result, destination register or memory address
    value, dest = exmem_read.value, exmem_read.dest

    # R-format
    if mem_write == 0 and mem_read == 0 and mem_to_reg == 0:
        memwb_write.set(value, dest, mem_to_reg)

    # NOP
    elif mem_write is None and mem_read is None and mem_to_reg is None:
        memwb_write.set(value, dest, mem_to_reg)

    # I-format
    else:
        # lb
        if mem_write == 0 and mem_read == 1 and mem_to_reg == 1:
            memwb_write.set(main_mem[value], dest, mem_to_reg) # type: ignore

        # sb
        elif mem_write == 1 and mem_read == 0 and mem_to_reg is None:
            reg_val = exmem_read.dest
            main_mem[value] = reg_val # type: ignore
            memwb_write.set(None, None, mem_to_reg)

def wb_stage(memwb_read: MemWb, regs: list[int]):
    # read the alu result and read dest register
    data, reg_dest = memwb_read.data, memwb_read.dest

    # write to register is R-format or LB
    if memwb_read.mem_to_reg == 0 or memwb_read.mem_to_reg == 1:
        regs[reg_dest] = data # type: ignore

def copy_write_to_read(
    write: IfId | IdEx | ExMem | MemWb,
    read: IfId | IdEx | ExMem | MemWb
):
    # if -> id
    if isinstance(write, IfId):
        read.set(write.get()) # type: ignore

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
                             memwb_write: MemWb, memwb_read: MemWb):
    print(f"Clock Cycle {index}\n")

    # IF/ID
    # write
    print(f"{RED_BG}IF/ID Write (written to by the IF stage){RESET}")
    print(f"Inst = 0x{ifid_write.instruction:08X}") # type: ignore
    # read
    print(f"{RED_BG}IF/ID Read (read by the ID stage){RESET}")
    print(f"Inst = 0x{(ifid_read.instruction if ifid_read.instruction else 00000000):08X}\n")

    # ID/EX
    # write
    print(f"{RED_BG}ID/EX Write (written to by the ID stage)")
    idex_write_output = (f"" if idex_write.opcode and idex_write.rs else f"Control = 0x"):08X
    print(f"(Control: RegDst = {idex_write.reg_dst} if )")

    print()

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
                             memwb_write, memwb_read)

        # write -> read copy over values
        copy_write_to_read(ifid_write, ifid_read)
        copy_write_to_read(idex_write, idex_read)
        copy_write_to_read(exmem_write, exmem_read)
        copy_write_to_read(memwb_write, memwb_read)

        


if __name__ == "__main__":
    main()