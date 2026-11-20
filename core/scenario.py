from pathlib import Path
import sqlite3
import shutil
import os
from fileInfo import info

"""
the code keeps growing aaah i can't stop it , it looking like a speghatti mama mia 
"""
class scenarios:
    def __init__(self):
        pass
    def newSetup(self,name):
        folder = Path(f"scenarios/{name}").mkdir(parents=True , exist_ok=True)

        with sqlite3.connect(f"scenarios/{name}/{name}.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT UNIQUE NOT NULL,
                sha256 TEXT UNIQUE NOT NULL
                )
            """)

        conn.close()    

    def openSetup(self,name):
        folder = Path("scenarios") / name
        db = folder / f"{name}.db"

        if not folder.is_dir():
            raise FileNotFoundError(f"The scenario folder does not exist: {folder}")
        if not db.is_file():
            raise FileNotFoundError(f"The scenario database does not exist: {db}")

        connection = sqlite3.connect(db)
        return folder, connection

    """
    screw os , me and my homeies us pathlib 
    """
    def addFile(self,filepath,folder,conn):
        filepath = Path(filepath)
        folder = Path(folder)

        destination = folder / filepath.name

        shutil.copy2(filepath, destination)

        file_name = filepath.name
        fileinfo = info(destination)

        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO files (filename,file_path,sha256)
                VALUES(?,?,?)
                """,
                (file_name,str(destination),fileinfo.computeHash())
            )
            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

