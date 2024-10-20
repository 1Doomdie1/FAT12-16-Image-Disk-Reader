class FAT:
    def __init__(self, raw_data: bytes) -> None:
        self.raw_data = raw_data
    
    def parse(self) -> list[int]:
        return [int.from_bytes(self.raw_data[i:i+2], "little") for i in range(0, len(self.raw_data), 2)]
