import hashlib
from pathlib import Path

class info:
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.name = self.filepath.name

        with self.filepath.open("rb") as file:
            self.hash = hashlib.file_digest(file, "sha256").hexdigest()
