from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from research_db.memorytier.engine import MemoryTierPolicy
from research_db.persist.ids import stable_id
DDL = Path(__file__).resolve().parents[2] / "sql" / "014_phase14_sqlite_twin.sql"
def _now():
    return datetime.now(timezone.utc).isoformat()
def install_phase14(self):
    self.conn.executescript(DDL.read_text(encoding="utf-8")); self.conn.commit()
def persist_memory_tiers(self, policy: MemoryTierPolicy):
    now = _now()
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate","phase14"),"phase":"phase14","approved":1,"ingestion_enabled":0,"notes":"Memory tiers raw retained","created_at":now})
        for p in policy.policies:
            self._upsert("research__memory_tier_policy", {"id": stable_id("mtp", p["code"]), "code": p["code"], "tier": p["tier"], "horizon": p["horizon"], "deletes_raw": 1 if p["deletes_raw"] else 0})
        for s in policy.summaries:
            self._upsert("research__memory_summary", {"id": stable_id("msum", s["code"]), "code": s["code"], "tier": s["tier"], "n": s["n"], "mean_close": s["mean_close"], "min_close": s["min_close"], "max_close": s["max_close"], "start_time": s["start"], "end_time": s["end"], "raw_retained": 1 if s["raw_retained"] else 0})
    return {"policies": self._count("research__memory_tier_policy"), "summaries": self._count("research__memory_summary")}
def bind(cls):
    cls.install_phase14 = install_phase14
    cls.persist_memory_tiers = persist_memory_tiers
