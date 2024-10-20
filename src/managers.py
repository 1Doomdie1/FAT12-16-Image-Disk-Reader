class FileReader:
    def __init__(self, path) -> None:
        self.path = path

    def read_bytes(self, offset=0, amount=512):
        with open(self.path, "rb") as f:
            f.seek(offset)
            return f.read(amount)