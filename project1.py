def main():
    # list of instructions
    instructions = [0x032BA020, 0x8CE90014, 0x12A90003, 0x022DA822, 0xADB30020, 0x02697824, 0xAE8FFFF4,
0x018C6020, 0x02A4A825, 0x158FFFF7, 0x8ECDFFF0]

    # instruction = 0x032BA020

    hex_address = 0x9A040

    for instruction in instructions:
        # mask for each field in instruction format
        opcode_mask = 0b11111100000000000000000000000000
        rs_mask = 0b00000011111000000000000000000000
        rt_mask = 0b00000000000111110000000000000000
        rd_mask = 0b00000000000000001111100000000000
        funct_mask = 0b00000000000000000000000000111111
        offset_mask = 0b00000000000000001111111111111111

        opcode = (instruction & opcode_mask) >> 26
        rs = (instruction & rs_mask) >> 21
        rt = (instruction & rt_mask) >> 16

        if opcode == 0:
            rd = (instruction & rd_mask) >> 11
            funct = instruction & funct_mask

            if funct == 0b100000:
                print(f"{hex(hex_address)} add ${rd}, ${rs}, ${rt}")
            elif funct == 0b100010:
                print(f"{hex(hex_address)} sub ${rd}, ${rs}, ${rt}")
            elif funct == 0b100100:
                print(f"{hex(hex_address)} and ${rd}, ${rs}, ${rt}")
            elif funct == 0b100101:
                print(f"{hex(hex_address)} or ${rd}, ${rs}, ${rt}")
            elif funct == 0b101010:
                print(f"{hex(hex_address)} slt ${rd}, ${rs}, ${rt}")

        else:
            offset = instruction & offset_mask

            if offset >= 0x8000:
                offset = offset - 0x10000

            if opcode == 0b100011:
                print(f"{hex(hex_address)} lw ${rt}, {offset} (${rs})")
            elif opcode == 0b101011:
                print(f"{hex(hex_address)} sw ${rt}, {offset} (${rs})")
            elif opcode == 0b000100:
                print(f"{hex(hex_address)} beq ${rs}, ${rt}, address ${hex(hex_address+(4*offset)+(0x4))}")
            elif opcode == 0b000101:
                print(f"{hex(hex_address)} bne ${rs}, ${rt}, address ${hex(hex_address+(4*offset)+(0x4))}")

        hex_address += 0x4


if __name__ == "__main__":
    main()