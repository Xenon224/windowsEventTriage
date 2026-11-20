import hashlib
from pathlib import Path

"""
omg such a cute function
"""
class info:
    def __init__(self, filepath):
        self.filepath = Path(filepath)

    def computeHash(self):
        with self.filepath.open("rb") as file:
            self.hash = hashlib.file_digest(file, "sha256").hexdigest()
            return self.hash
