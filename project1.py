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

        # get value after mask and shift
        opcode = (instruction & opcode_mask) >> 26
        rs = (instruction & rs_mask) >> 21
        rt = (instruction & rt_mask) >> 16

        # format hex address without '0x' as the prefix
        formatted_hex_address = format(hex_address, "X")

        # R-format
        if opcode == 0:
            # get value after mask and shift
            rd = (instruction & rd_mask) >> 11
            funct = instruction & funct_mask

            # add funct
            if funct == 0b100000:
                print(f"{formatted_hex_address} add ${rd}, ${rs}, ${rt}")
            # sub funct
            elif funct == 0b100010:
                print(f"{formatted_hex_address} sub ${rd}, ${rs}, ${rt}")
            # and funct
            elif funct == 0b100100:
                print(f"{formatted_hex_address} and ${rd}, ${rs}, ${rt}")
            # or funct
            elif funct == 0b100101:
                print(f"{formatted_hex_address} or ${rd}, ${rs}, ${rt}")
            # slt funct
            elif funct == 0b101010:
                print(f"{formatted_hex_address} slt ${rd}, ${rs}, ${rt}")
        # I-format
        else:
            # get value after mask
            offset = instruction & offset_mask

            # check if offset value is bigger than or equal to 2^15 and then subtract 2^16 to get signed value. 

            if offset >= 0x8000:
                offset = offset - 0x10000

            # format hex address without '0x' as the prefix
            formatted_branch_address = format(hex_address+(4*offset)+(0x4), "X")

            # lw opcode
            if opcode == 0b100011:
                print(f"{formatted_hex_address} lw ${rt}, {offset} (${rs})")
            # sw opcode
            elif opcode == 0b101011:
                print(f"{formatted_hex_address} sw ${rt}, {offset} (${rs})")
            # beq opcode
            elif opcode == 0b000100:
                print(f"{formatted_hex_address} beq ${rs}, ${rt}, address {formatted_branch_address}")
            # bne opcode
            elif opcode == 0b000101:
                print(f"{formatted_hex_address} bne ${rs}, ${rt}, address {formatted_branch_address}")

        hex_address += 0x4


if __name__ == "__main__":
    main()