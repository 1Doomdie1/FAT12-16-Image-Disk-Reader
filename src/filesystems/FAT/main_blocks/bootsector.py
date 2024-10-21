class Bootsector:
    def __init__(self, bytes: bytes) -> None:
        self.bytes = bytes

    def fat_size(self) -> int:
        return int.from_bytes(self.bytes[0x16:0x18], "little") * int.from_bytes(self.bytes[0x0B:0x0D], "little")

    def fat_offset(self) -> int:
        return int.from_bytes(self.bytes[0x0E:0x10], "little") * int.from_bytes(self.bytes[0x0B:0x0D], "little")
    
    def jump_code(self) -> str:
        return self.bytes[0x0:0x3].hex(" ").upper()
    
    def oem(self) -> str:
        return self.bytes[0x3: 0x0B].decode("utf-8")
    
    def bytes_per_sector(self) -> int:
        return int.from_bytes(self.bytes[0x0B:0x0D], "little")

    def sectors_per_cluster(self) -> int:
        return int.from_bytes(self.bytes[0x0D:0x0E], "little")
    
    def reserved_sectors(self) -> int:
        return int.from_bytes(self.bytes[0x0E:0x10], "little")
    
    def fat_count(self) -> int:
        return int.from_bytes(self.bytes[0x10:0x11], "little")

    def rd_entries_count(self) -> int:
        return int.from_bytes(self.bytes[0x11:0x13], "little")
    
    def sectors_count(self) -> int:
        return int.from_bytes(self.bytes[0x13:0x15], "little") or int.from_bytes(self.bytes[0x20:0x24], "little")
    
    def disk_type(self) -> str:
        return self.bytes[0x15:0x16].hex().upper()
    
    def sectors_per_fat(self) -> int:
        return int.from_bytes(self.bytes[0x16:0x18], "little")
    
    def sectors_per_track(self) -> int:
        return int.from_bytes(self.bytes[0x18:0x1A], "little")
    
    def rd_offset(self) -> int:
        return (self.reserved_sectors() + self.sectors_per_fat() * self.fat_count()) * self.bytes_per_sector()
    
    def rd_size(self) -> int:
        return self.rd_entries_count() * 32


    def data(self):
        return {
            "Jump Code": self.jump_code(),
            "OEM": self.oem(),
            "Bytes Per Sector": self.bytes_per_sector(),
            "Sectors Per Cluster": self.sectors_per_cluster(),
            "Reserved Sectors": self.reserved_sectors(),
            "FAT Count": self.fat_count(),
            "Root Entries Count": self.rd_entries_count(),
            "Sectors Count": self.sectors_count(),
            "Disk Type": self.disk_type(),
            "Sectors Per FAT": self.sectors_per_fat(),
            "Sectors Per Track": self.sectors_per_track()
        }