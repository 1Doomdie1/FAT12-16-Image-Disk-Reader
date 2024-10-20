class Entry:
    def __init__(self, bytes: bytes):
        self.entry_data = [bytes[i:i+32] for i in range(0, len(bytes), 32)]
    
    def raw(self):
        return self.entry_data

    def name(self) -> str:
        name = ""
        if len(self.entry_data) > 1:
            for name_chuncks in self.entry_data[:-1][::-1]:
                name_parts = (name_chuncks[0x1 :0x10], name_chuncks[0xE :0x19], name_chuncks[0x1C:0x1F])
                for name_part in name_parts:
                    for i in range(0, len(name_part), 2):
                        if name_part[i:i+2] in (b'\x0f\x00', b'\xff\xff', b'\xff\xf8', b'\xff\xf7', b'\xff'): break
                        name += name_part[i:i+2].decode("utf-8")
        else:
            name = f'{self.entry_data[0][:8].decode("utf-8").strip()}{"." if self.entry_data[0][11] == 0x20 else ""}{self.entry_data[0][8:11].decode("utf-8")}'
        return name.replace("\x00", "").strip()

    def perms(self) -> tuple[str, str]:
        flag_value = self.entry_data[-1][11]
        return "r/-" if flag_value & 0x01 else "r/w"
    
    def type(self) -> str:
        flag_value = self.entry_data[-1][11]
        
        flags = {
            0x02: "Hidden",
            0x04: "System File",
            0x08: "Volume Label",
            0x10: "Directory",
            0x20: "File"
        }

        return ' '.join(desc for flag, desc in flags.items() if flag_value & flag)

    def size(self) -> int:
        return int.from_bytes(self.entry_data[-1][0x1C:0x1F], "little")

    def status(self) -> str:
        return "Deleted" if self.entry_data[-1][0] in (0x0, 0xE5) else "Present"

    def starting_cluster(self) -> int:
        cl_high = int.from_bytes(self.entry_data[-1][0x14:0x16], "little")
        cl_low  = int.from_bytes(self.entry_data[-1][0x1A:0x1C], "little")
        return cl_high if cl_high != 0 else cl_low

    def created_at(self) -> str:
        hms = self.__decode_dos_time(self.entry_data[-1][13:15])
        day = self.__decode_dos_date(self.entry_data[-1][16:18])
        return f"{day} - {hms}"

    def accessed_at(self) -> str:
        return self.__decode_dos_date(self.entry_data[-1][18:20])

    def written_at(self) -> str:
        hms = self.__decode_dos_time(self.entry_data[-1][22:24])
        day = self.__decode_dos_date(self.entry_data[-1][24:26])
        return f"{day} - {hms}"

    def cluster_chain(self, fat_structure: list) -> list:
        chain = [self.starting_cluster()]
        next_cluster = fat_structure[self.starting_cluster()]
        while True:
            if next_cluster in (65535, 65528, 0): break
            chain.append(next_cluster)
            next_cluster = fat_structure[next_cluster]
        return chain

    def sector_chain(self, fat_structure: list, cl2_offset: int, sectors_per_cluster: int) -> list:
        return [ (abs(cluster - 2)  * sectors_per_cluster + cl2_offset) if cluster else cl2_offset - 32 for cluster in self.cluster_chain(fat_structure)]

    def __decode_dos_time(self, value) -> str:
        value = int.from_bytes(value, "little")
        hours = str((value >> 11) & 0x1F).rjust(2, "0")
        minutes = str((value >> 5) & 0x3F).rjust(2, "0")
        seconds = str((value & 0x1F) * 2).rjust(2, "0")
        return f"{hours}:{minutes}:{seconds}"

    def __decode_dos_date(self, value) -> str:
        value = int.from_bytes(value, "little")
        day = str(value & 0x1F).rjust(2, "0")
        month = str((value >> 5) & 0x0F).rjust(2, "0")
        year = str((value >> 9) + 1980)
        return f"{day}/{month}/{year if int(day) and int(month) else '0000'}"

    def data(self):
        return {
            "name": self.name(),
            "type": self.type(),
            "size": self.size(),
            "status": self.status(),
            "permissions": self.perms(),
            "starting_cluster": self.starting_cluster(),
            "created_at": self.created_at(),
            "accessed_at": self.accessed_at(),
            "written_at": self.written_at()
        }
