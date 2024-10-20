from src.filesystems.FAT.parsers.entry import Entry

class DirParser:
    def __init__(self, bytes: bytes):
        self.bytes = bytes

    def entries(self) -> list[Entry]:
        entries = []
        pointer = 0

        while True:
            if pointer >= len(self.bytes): break

            chunck = self.bytes[pointer:pointer+32]
            if chunck == b"\00" * 32: break

            if chunck[11] != 0x0F:
                entries.append(Entry(chunck))
                pointer += 32
            elif chunck[0] not in (0x0, 0xE5) and chunck[11] == 0x0F:
                chunck_size = (0x40 ^ chunck[0] + 1) * 32
                entries.append(Entry(self.bytes[pointer:pointer+chunck_size]))
                pointer += chunck_size
            elif chunck[0] in (0x0, 0xE5) and chunck[11] == 0x0F:
                entry_sig = chunck[13]
                offset = 32
                while True:
                    new_chunck = self.bytes[pointer:pointer+offset]
                    if new_chunck[-19] == entry_sig:
                        offset += 32
                    else:
                        entries.append(Entry(new_chunck))
                        break
                pointer += offset
        return entries

    def get_entry(self, name:str, type: list = ["*"]) -> Entry | None:
        for entry in self.entries():
            if (entry.name() == name) and (entry.type() in type if type[0] != "*" else True):
                return entry
        return None  
