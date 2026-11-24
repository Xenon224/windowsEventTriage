from pathlib import Path
import Evtx.Evtx as evtx
from lxml import etree
import pandas as pd
import sqlite3 ,json

namespace = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}
# yes microsoft , stuck in the 2k are we?

class digestion:
    def __init__(self,scenario):
        self.folder = Path(f"scenarios/{scenario}")
        self.errors = 0
        self.con = sqlite3.connect(str(self.folder / "events.db"))

        self.con.execute("PRAGMA journal_mode=WAL")
        self.con.execute("PRAGMA synchronous=NORMAL")
        
        self.con.execute("""
        CREATE TABLE IF NOT EXISTS events (
            timestamp TIMESTAMP, event_id INTEGER, provider VARCHAR,
            channel VARCHAR, computer VARCHAR, record_id BIGINT,
            level INTEGER, user_sid VARCHAR, source_file VARCHAR,
            data JSON, raw_xml VARCHAR,
            PRIMARY KEY (computer, channel, record_id)
        )""")

    def ingestFile(self,file):
        file_path = self.folder / file

        with evtx.Evtx(file_path) as openFile:

            for record in openFile.records():
                try:
                    raw_xml = record.xml() # raw data 
                    root = etree.fromstring(record.xml().encode("utf-8")) #root of the xml tree
                    s = root.find('ns:System', namespace)# iykyk

                    #-- data --
                    # THIS SHIT AI . lord i was gonna parse the xml with [0] and miss other values ifykyk

                    data = {}
                    def add_data_field(key, value):
                        base, suffix = key, 2
                        while key in data:
                            key = f"{base}_{suffix}"
                            suffix += 1
                        data[key] = value

                    event_data = root.find('ns:EventData', namespace)
                    if event_data is not None:
                        for i, child in enumerate(event_data):
                            key = child.get("Name") or f"param{i}"
                            add_data_field(key, child.text)

                    user_data = root.find('ns:UserData', namespace)
                    if user_data is not None and len(user_data):
                        for child in user_data[0]:
                            add_data_field(etree.QName(child).localname, child.text)

                    #end of ai :]

                    sec = s.find('ns:Security', namespace)

                    yield {
                        "timestamp": pd.to_datetime(s.find('ns:TimeCreated', namespace).get("SystemTime"), utc=True),
                        "event_id": int(s.find('ns:EventID', namespace).text),
                        "provider": s.find('ns:Provider', namespace).get("Name"),
                        "channel": s.find('ns:Channel', namespace).text,
                        "computer": s.find('ns:Computer', namespace).text,
                        "record_id": int(s.find('ns:EventRecordID', namespace).text),
                        "level": int(s.find('ns:Level', namespace).text),
                        "user_sid": sec.get("UserID") if sec is not None else None,
                        "source_file": str(file),
                        "data": data,
                        "raw_xml": raw_xml,
                    }
                except Exception as e:
                    self.errors += 1

    # insert ze batch into ze database ya 
    def insertBatch(self,batch):
        rows = [(
        r["timestamp"].isoformat(), r["event_id"], r["provider"],
        r["channel"], r["computer"], r["record_id"], r["level"],
        r["user_sid"], r["source_file"], json.dumps(r["data"]), r["raw_xml"]) for r in batch]
       
        self.con.executemany("INSERT OR IGNORE INTO events VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows)
       
        self.con.commit()

    #storing in batches - so doesn't load everything into memory at once and query db for each record
    def store(self, file):
        batch = []
        for rec in self.ingestFile(file):
            batch.append(rec)
            if len(batch) >= 10000:
                self.insertBatch(batch)
                batch = []
        if batch: # remaning left over batch
            self.insertBatch(batch)
        


if __name__ == "__main__":
    obj = digestion("example2")
    obj.store("Security.evtx")
    obj.con.close()

