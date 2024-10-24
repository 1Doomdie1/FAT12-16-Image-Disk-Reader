class Entry_Hex_Parser:
    NAME_COLOR        = "[blue]"
    ALLOC_N_SEQ       = "[grey58]"
    ALLOC_STATUS      = "[green]"
    DE_ALLOC_STATUS   = "[red3]"
    ENTRY_SIG_COLOR   = "[magenta]"
    ENTRY_TYPE_COLOR  = "[green_yellow]"
    TENTHS_OF_S_COLOR = "[orange3]"
    HMS_COLOR         = "[orange3]"
    CREATED_AT_COLOR  = "[orange3]"
    ACCESS_DAY_COLOR  = "[orange3]"
    CL_HIGH_COLOR     = "[bright_green]"
    WRITTEN_AT_COLOR  = "[orange3]"
    CL_LOW_COLOR      = "[bright_green]"
    SIZE_COLOR        = "[turquoise2]"

    def __parse_lfn_bytes(self, data: bytes) -> tuple:
        ret = ()
        chuncks = (data[i:i+32] for i in range(0, len(data), 32))
        for chunck in chuncks:
            # FIRST 16 bytes
            alloc_n_seq   = self.__color_byte(chunck[    0    ],                  self.ALLOC_N_SEQ if chunck[0] not in (0x0, 0xE5) else self.DE_ALLOC_STATUS)
            name_part_1   = self.__color_txt (chunck[0x01:0x0B].hex(" ").upper(), self.NAME_COLOR)
            entry_type    = self.__color_byte(chunck[   0xB   ],                  self.ENTRY_TYPE_COLOR)
            reserved_1    = self.__color_byte(chunck[   0XC   ])
            entry_sig     = self.__color_byte(chunck[   0xD   ],                  self.ENTRY_SIG_COLOR)
            name_part_2   = self.__color_txt (chunck[0x0E:0x10].hex(" ").upper(), self.NAME_COLOR)
            decoded_hex_1 = " ".join(self.__color_txt(chr(i), self.NAME_COLOR) if 35 <= i <= 126 else "." for i in chunck[:0x10])

            # NEXT 16 bytes
            name_part_3 = self.__color_txt (chunck[0x10:0x1A].hex(" ").upper(), self.NAME_COLOR)
            reserved_2  = self.__color_txt (chunck[0x1A:0x1C].hex(" ").upper())
            name_part_4 = self.__color_txt (chunck[0x1C:    ].hex(" ").upper(), self.NAME_COLOR)
            decoded_hex_2 = " ".join(self.__color_txt(chr(i), self.NAME_COLOR) if 35 <= i <= 126 else "." for i in chunck[0x10:])

            ret += (
                (f"{alloc_n_seq} {name_part_1} {entry_type} {reserved_1} {entry_sig} {name_part_2}", decoded_hex_1),
                (f"{name_part_3} {reserved_2} {name_part_4}", decoded_hex_2)
            )

        return ret

    def __parse_sfn_bytes(self, data: bytes) -> tuple:
        # FIRST 16 bytes
        alloc_status  = self.__color_byte(data[    0    ], self.ALLOC_STATUS if data[0] not in (0x0, 0xE5) else self.DE_ALLOC_STATUS)
        name          = self.__color_txt (data[0x01:0x0B].hex(" ").upper(), self.NAME_COLOR                                         )
        file_attr     = self.__color_byte(data[   0xB   ],                  self.ENTRY_TYPE_COLOR                                   )
        reserved      = self.__color_byte(data[   0xC   ]                                                                           )
        tenths_of_sec = self.__color_byte(data[   0xD   ],                  self.TENTHS_OF_S_COLOR                                  )
        hms           = self.__color_txt (data[0x0E:0x10].hex(" ").upper(), self.HMS_COLOR                                          )
        decoded_hex_1 = " ".join(self.__color_txt(chr(i), self.NAME_COLOR) if 35 <= i <= 126 else "." for i in data[:0x10]          )

        # NEXT 16 Bytes
        create_day    = self.__color_txt (data[0x10:0x12].hex(" ").upper(), self.CREATED_AT_COLOR)
        access_day    = self.__color_txt (data[0x12:0x14].hex(" ").upper(), self.ACCESS_DAY_COLOR)
        cluster_high  = self.__color_txt (data[0x14:0x16].hex(" ").upper(), self.CL_HIGH_COLOR   )
        written_time  = self.__color_txt (data[0x16:0x18].hex(" ").upper(), self.WRITTEN_AT_COLOR)
        cluster_low   = self.__color_txt (data[0x18:0x1A].hex(" ").upper(), self.CL_LOW_COLOR    )
        size          = self.__color_txt (data[0x1A:    ].hex(" ").upper(), self.SIZE_COLOR      )
        decoded_hex_2 = " ".join(self.__color_txt(chr(i), self.NAME_COLOR) if 33 <= i <= 126 else "." for i in data[0x10:])

        return (
            (f"{alloc_status} {name} {file_attr} {reserved} {tenths_of_sec} {hms}", decoded_hex_1),
            (f"{create_day} {access_day} {cluster_high} {written_time} {cluster_low} {size}", decoded_hex_2)
        )

    def hex_view(self, entry: bytes) -> str:
        lfn_name = self.__parse_lfn_bytes(entry[:-32]) if len(entry) > 32 else None
        sfn = self.__parse_sfn_bytes(entry[-32:])
        return lfn_name + sfn if lfn_name else sfn

    def __color_txt(self, txt: str, color: str = "") -> str:
        return '{}{}{}'.format(
            color, 
            txt.replace("\\", "."),
            color.replace("[", "[/")
        )

    def __color_byte(self, byte: int, color: str = "") -> str:
        return self.__color_txt(hex(byte)[2:].upper().rjust(2, "0"), color)
