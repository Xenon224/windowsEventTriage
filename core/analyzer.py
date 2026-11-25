import sqlite3
from pathlib import Path
import yaml
import json

# define individual operation becuse my code is lazy and my rules is layzier
OPS = {
    "equals":       lambda a, w: a == w,
    "not_equals":   lambda a, w: a != w,
    "contains":     lambda a, w: w in a,
    "startswith":   lambda a, w: a.startswith(w),
    "endswith":     lambda a, w: a.endswith(w),
    "not_endswith": lambda a, w: not a.endswith(w),
    "in":           lambda a, w: a in w,
}

class analyze:
    def __init__(self,scenario):
        self.folder = Path(f"scenarios/{scenario}")
        self.con = sqlite3.connect(str(self.folder / "events.db"))
        self.rulesPath = "core/rules.yaml"

    def runAgainstRules(self):
        rules = yaml.safe_load(open(self.rulesPath))["rules"]

        self.con.row_factory = sqlite3.Row

        findings = []

        for rule in rules:
            rows = self.con.execute("SELECT * FROM events WHERE event_id = ?", (rule["event_id"],))

            for row in rows:
                data = json.loads(row["data"])

                matched = True

                for condition in rule.get("conditions", []):
                    actual = str(data.get(condition["field"],""))

                    if not OPS[condition["op"]](actual,condition["value"]):
                        matched = False
                        break

                if matched:
                    findings.append({
                "rule_id": rule["id"],
                "title": rule["title"],
                "severity": rule["severity"],
                "timestamp": row["timestamp"],
                "record_id": row["record_id"],
                "data": data,
            })

        json.dump(findings, open(f"{self.folder}/findings.json", "w"), indent=2)

