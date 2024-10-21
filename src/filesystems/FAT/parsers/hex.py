from colorama import Style, Fore, init, Back
init(autoreset=True)

class Entry_Hex_Parser:
    def __init__(self, entry):
        self.entry = entry
    
    def hex_view(self) -> str:
        NAME_COLOR            = Fore.BLUE
        ENTRY_SIG_COLOR       = Fore.RED
        ENTRY_TYPE_COLOR      = Fore.YELLOW
        ENTRY_SIZE_BYTE_COLOR = Fore.GREEN
        OUTER_FRAME = f'+{"-" * 10}+{"-" * 49}+{"-" * 33}+'

        temp = ""

        for i in range(0, len(self.entry), 16):
            padding = self.color_txt("0".rjust(8 - len(hex(i)[2:]), "0"), Fore.BLACK)
            offset = self.color_txt(hex(i)[2:], Fore.CYAN)
            decoded = " ".join([ self.color_txt(chr(j), NAME_COLOR) if 33 <= j <= 126 else "." for j in self.entry[i:i+16]])

            if len(self.entry) > 32:
                if (i//16 + 1) % 2 != 0 and i < len(self.entry) - 32:
                    name_part_1     = self.color_txt(self.entry[i:i+16][0x1:0xB].hex(" ").upper(), NAME_COLOR)
                    name_part_2     = self.color_txt(self.entry[i:i+16][0xE:   ].hex(" ").upper(), NAME_COLOR)
                    entry_size_byte = self.color_txt(hex(self.entry[i:i+16][0] )[2:].rjust(2, '0').upper(), ENTRY_SIZE_BYTE_COLOR if self.entry[i:i+16][0] not in (0x0, 0xE5) else Fore.MAGENTA)
                    entry_type      = self.color_txt(hex(self.entry[i:i+16][11])[2:].rjust(2, '0').upper(), ENTRY_TYPE_COLOR)
                    entry_sig       = self.color_txt(hex(self.entry[i:i+16][13])[2:].rjust(2, '0').upper(), ENTRY_SIG_COLOR)
                    line = f"{entry_size_byte} {name_part_1} {entry_type} {hex(self.entry[i:i+16][12])[2:].rjust(2, '0').upper()} {entry_sig} {name_part_2}"
                elif (i//16 + 1) % 2 == 0 and i < len(self.entry) - 32:
                    name_part_1 = self.color_txt(self.entry[i:i+16][ : 10].hex(" ").upper(), NAME_COLOR)
                    name_part_2 = self.color_txt(self.entry[i:i+16][-4: ].hex(" ").upper(), NAME_COLOR)
                    line = f"{name_part_1} {self.entry[i:i+16][10:12].hex(' ').upper()} {name_part_2}"
                elif (i//16 + 1) % 2 != 0 and i >= len(self.entry) - 32:
                    alocation_status         = self.color_txt(hex(self.entry[i:i+16][0])[2:].rjust(2, "0").upper(), Fore.MAGENTA)
                    name                     = self.color_txt(self.entry[i:i+16][0x01:0xB].hex(" ").upper(), NAME_COLOR)
                    file_attribute           = self.color_txt(hex(self.entry[i:i+16][0xB])[2:].rjust(2, "0").upper(), Fore.BLACK)
                    reserved                 = hex(self.entry[i:i+16][0xC])[2:].rjust(2, "0").upper()
                    create_tenths_of_seconds = hex(self.entry[i:i+16][0xD])[2:].rjust(2, "0").upper()
                    create_hms               = self.entry[i:i+16][0xE:].hex(" ").upper()
                    line = f"{alocation_status} {name} {file_attribute} {reserved} {create_tenths_of_seconds} {create_hms}"
                elif (i//16 + 1) % 2 == 0 and i >= len(self.entry) - 32:
                    create_day   = self.entry[i:i+16][   :0x3].hex(" ").upper()
                    access_day   = self.entry[i:i+16][0x3:0x4].hex(" ").upper()
                    high_cl      = self.entry[i:i+16][0x4:0x6].hex(" ").upper()
                    written_time = self.entry[i:i+16][0x6:0x8].hex(" ").upper()
                    written_day  = self.entry[i:i+16][0x8:0xA].hex(" ").upper()
                    low_day      = self.entry[i:i+16][0xA:0xC].hex(" ").upper()
                    size         = self.entry[i:i+16][0xC:   ].hex(" ").upper()
                    line = f"{create_day} {access_day} {high_cl} {written_time} {written_day} {low_day} {size}"
            elif (i//16 + 1) % 2 != 0:
                alocation_status         = self.color_txt(hex(self.entry[i:i+16][0])[2:].rjust(2, "0").upper(), Fore.MAGENTA)
                name                     = self.color_txt(self.entry[i:i+16][0x01:0xB].hex(" ").upper(), NAME_COLOR)
                file_attribute           = self.color_txt(hex(self.entry[i:i+16][0xB])[2:].rjust(2, "0").upper(), Fore.BLACK)
                reserved                 = hex(self.entry[i:i+16][0xC])[2:].rjust(2, "0").upper()
                create_tenths_of_seconds = hex(self.entry[i:i+16][0xD])[2:].rjust(2, "0").upper()
                create_hms               = self.entry[i:i+16][0xE:].hex(" ").upper()
                line = f"{alocation_status} {name} {file_attribute} {reserved} {create_tenths_of_seconds} {create_hms}"
            elif (i//16 + 1) % 2 == 0 and i >= len(self.entry) - 32:
                create_day   = self.entry[i:i+16][   :0x3].hex(" ").upper()
                access_day   = self.entry[i:i+16][0x3:0x4].hex(" ").upper()
                high_cl      = self.entry[i:i+16][0x4:0x6].hex(" ").upper()
                written_time = self.entry[i:i+16][0x6:0x8].hex(" ").upper()
                written_day  = self.entry[i:i+16][0x8:0xA].hex(" ").upper()
                low_day      = self.entry[i:i+16][0xA:0xC].hex(" ").upper()
                size         = self.entry[i:i+16][0xC:   ].hex(" ").upper()
                line = f"{create_day} {access_day} {high_cl} {written_time} {written_day} {low_day} {size}"
            temp += f"| {padding+offset} | {line} | {decoded} |\n"
        return f"{OUTER_FRAME}\n{temp}{OUTER_FRAME}"

    def color_txt(self, txt: str, color: str) -> str:
        return f'{color}{txt}{Style.DIM}{Style.RESET_ALL}'

