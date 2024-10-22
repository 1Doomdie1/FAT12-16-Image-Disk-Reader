from colorama import Style, Fore, init
init(autoreset=True)

class Entry_Hex_Parser:
    NO_COLOR         = Fore.RESET
    NAME_COLOR       = Fore.BLUE
    ALLOC_N_SEQ      = Fore.BLACK
    ALLOC_STATUS     = Fore.GREEN
    DE_ALLOC_STATUS  = Fore.RED
    ENTRY_SIG_COLOR  = Fore.MAGENTA
    ENTRY_TYPE_COLOR = Fore.YELLOW

    def __parse_lfn_name(self, data: bytes) -> tuple:
        ret = ()
        chuncks = (data[i:i+32] for i in range(0, len(data), 32))
        for chunck in chuncks:
            alloc_n_seq   = self.__color_byte(chunck[    0    ],                  self.ALLOC_N_SEQ if chunck[0] not in (0x0, 0xE5) else self.DE_ALLOC_STATUS)
            name_part_1   = self.__color_txt (chunck[0x01:0x0B].hex(" ").upper(), self.NAME_COLOR)
            entry_type    = self.__color_byte(chunck[   0xB   ],                  self.ENTRY_TYPE_COLOR)
            reserved_1    = self.__color_byte(chunck[   0XC   ])
            entry_sig     = self.__color_byte(chunck[   0xD   ],                  self.ENTRY_SIG_COLOR)
            name_part_2   = self.__color_txt (chunck[0x0E:0x10].hex(" ").upper(), self.NAME_COLOR)
            decoded_hex_1 = " ".join(self.__color_txt(chr(i), self.NAME_COLOR) if 33 <= i <= 126 else "." for i in chunck[:0x10])

            name_part_3 = self.__color_txt (chunck[0x10:0x1A].hex(" ").upper(), self.NAME_COLOR)
            reserved_2  = self.__color_txt (chunck[0x1A:0x1C].hex(" ").upper())
            name_part_4 = self.__color_txt (chunck[0x1C:    ].hex(" ").upper(), self.NAME_COLOR)
            decoded_hex_2 = " ".join(self.__color_txt(chr(i), self.NAME_COLOR) if 33 <= i <= 126 else "." for i in chunck[0x10:])

            ret += (
                f"{alloc_n_seq} {name_part_1} {entry_type} {reserved_1} {entry_sig} {name_part_2} | {decoded_hex_1}",
                f"{name_part_3} {reserved_2} {name_part_4} | {decoded_hex_2}"
            )
        return ret

    def __parse_sfn_bytes(self, data: bytes) -> tuple:
        alloc_status  = self.__color_byte(data[    0    ], self.ALLOC_STATUS if data[0] not in (0x0, 0xE5) else self.DE_ALLOC_STATUS)
        name          = self.__color_txt (data[0x01:0x0B].hex(" ").upper(), self.NAME_COLOR)
        file_attr     = self.__color_byte(data[   0xB   ],                  self.ENTRY_TYPE_COLOR)
        reserved      = self.__color_byte(data[   0xC   ])
        tenths_of_sec = self.__color_byte(data[   0xD   ]) # TODO: Add colors for those bytes
        hms           = self.__color_txt (data[0x0E:0x10].hex(" ").upper())
        decoded_hex_1 = " ".join(self.__color_txt(chr(i), self.NAME_COLOR) if 33 <= i <= 126 else "." for i in data[:0x10])

        # TODO: Add colors for those bytes
        create_day    = self.__color_txt (data[0x10:0x12].hex(" ").upper())
        access_day    = self.__color_txt (data[0x12:0x14].hex(" ").upper())
        cluster_high  = self.__color_txt (data[0x14:0x16].hex(" ").upper())
        written_time  = self.__color_txt (data[0x16:0x18].hex(" ").upper())
        cluster_low   = self.__color_txt (data[0x18:0x1A].hex(" ").upper())
        size          = self.__color_txt (data[0x1A:    ].hex(" ").upper())
        decoded_hex_2 = " ".join(self.__color_txt(chr(i), self.NAME_COLOR) if 33 <= i <= 126 else "." for i in data[0x10:])

        return (
            f"{alloc_status} {name} {file_attr} {reserved} {tenths_of_sec} {hms} | {decoded_hex_1}",
            f"{create_day} {access_day} {cluster_high} {written_time} {cluster_low} {size} | {decoded_hex_2}"
        )

    def hex_view(self, entry: bytes) -> str:
        OUTER_FRAME = f'+{"-" * 10}+{"-" * 49}+{"-" * 33}+'
        lfn_name = self.__parse_lfn_name(entry[:-32]) if len(entry) > 32 else None
        sfn = self.__parse_sfn_bytes(entry[-32:])

        # This is just madness lol
        # This is the table structure 
        # | pad offset |                       hex                       |             decoded             |
        # | 0000000  0 | 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 | . . . . . . . . . . . . . . . . |

        table = "\n".join(f'| {self.__color_txt("0" * (8 - len(hex(i)[:2]) if i else 7), Fore.BLACK)}{self.__color_txt(hex(i*16)[2:])} | {line} |' for i, line in  enumerate(lfn_name + sfn if lfn_name else sfn))
        return f"{OUTER_FRAME}\n{table}\n{OUTER_FRAME}"

    def __color_txt(self, txt: str, color: str = NO_COLOR) -> str:
        return f'{color}{txt}{Style.RESET_ALL}'

    def __color_byte(self, byte: int, color: str = NO_COLOR) -> str:
        return self.__color_txt(hex(byte)[2:].upper().rjust(2, "0"), color)