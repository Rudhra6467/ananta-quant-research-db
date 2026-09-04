from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from research_db.paper.engine import PaperLedger
from research_db.persist.ids import stable_id
DDL = Path(__file__).resolve().parents[2] / "sql" / "018_phase18_sqlite_twin.sql"
def _now():
    return datetime.now(timezone.utc).isoformat()
def install_phase18(self):
    self.conn.executescript(DDL.read_text(encoding="utf-8")); self.conn.commit()
def persist_paper(self, ledger: PaperLedger):
    now = _now()
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate","phase18"),"phase":"phase18","approved":1,"ingestion_enabled":0,"notes":"Paper ledger","created_at":now})
        for p in ledger.profiles:
            self._upsert("research__operating_profile", {"id": stable_id("prof", p["code"]), "code": p["code"], "max_risk": p["max_risk"], "live_capital": 1 if p["live_capital"] else 0})
        for i, d in enumerate(ledger.decisions):
            self._upsert("research__paper_decision", {"id": stable_id("pdec", d["profile"], d["action"], d["knowledge_time"], str(i)), "profile_code": d["profile"], "action": d["action"], "knowledge_time": d["knowledge_time"], "reason": d["reason"], "query_name": d.get("query"), "capital": d["capital"]})
    return {"profiles": self._count("research__operating_profile"), "decisions": self._count("research__paper_decision")}
def bind(cls):
    cls.install_phase18 = install_phase18
    cls.persist_paper = persist_paper
