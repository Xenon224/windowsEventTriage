from pathlib import Path
import Evtx.Evtx as evtx
from lxml import etree
import pandas as pd
import duckdb ,json
#choose duckdb instead of sql , it's better for analystics . source - google and ai overview :/

namespace = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}
# yes microsoft , stuck in the 2k are we?

class digestion:
    def __init__(self,scenario):
        self.folder = Path(f"scenarios/{scenario}")
        self.errors = 0
        self.con = duckdb.connect(str(self.folder / "events.duckdb"))
        
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
                    data = {}
                    # ngl never though of this thanks ai , otherwise i would have had to do list with [0] >:[
                    container = root.find('ns:EventData',namespace)
                    if container is not None:
                        for i,child in enumerate(container):
                            key = child.get("Name") or f"param{i}"
                            base,n = key,2

                            while key in data :
                                key = f"{base}_{n}"
                                n += 1
                                data[key] = child.text
                            else:
                                ud = root.find('ns:UserData', namespace)
                                if ud is not None and len(ud):
                                    for child in ud[0]:
                                        data[etree.QName(child).localname] = child.text

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
        df = pd.DataFrame(batch)
        df["timestamp"] = df["timestamp"].dt.tz_convert(None)# keep the og utc 
        df["data"] = df["data"].apply(json.dumps)

        # dude thank god for ai did these queries i kept messing it up :'[
        self.con.execute("""
        INSERT OR IGNORE INTO events
        SELECT timestamp, event_id, provider, channel, computer, record_id,
               level, user_sid, source_file, data, raw_xml FROM df""")

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
