from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from research_db.expansion.engine import ExpansionRegistry
from research_db.persist.ids import stable_id
DDL19 = Path(__file__).resolve().parents[2] / "sql" / "019_phase19_sqlite_twin.sql"
DDL20 = Path(__file__).resolve().parents[2] / "sql" / "020_phase20_sqlite_twin.sql"
def _now():
    return datetime.now(timezone.utc).isoformat()
def install_phase19(self):
    self.conn.executescript(DDL19.read_text(encoding="utf-8")); self.conn.commit()
def install_phase20(self):
    self.conn.executescript(DDL20.read_text(encoding="utf-8")); self.conn.commit()
def persist_expansion(self, registry=None):
    registry = registry or ExpansionRegistry()
    now = _now()
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate","phase19"),"phase":"phase19","approved":1,"ingestion_enabled":0,"notes":"Universe plan","created_at":now})
        self._upsert("ops__schema_gate", {"id": stable_id("gate","phase20"),"phase":"phase20","approved":1,"ingestion_enabled":0,"notes":"Market DB plan","created_at":now})
        for u in registry.universes:
            self._upsert("ops__universe_plan", {"id": stable_id("uni", u["code"]), "code": u["code"], "target_assets": u["assets"], "target_years": u["years"], "ingested": 1 if u["ingested"] else 0})
        for m in registry.markets:
            self._upsert("ops__market_database_plan", {"id": stable_id("mdb", m["code"]), "code": m["code"], "horizon": m["horizon"], "created": 1 if m["created"] else 0})
    return {"universes": self._count("ops__universe_plan"), "markets": self._count("ops__market_database_plan")}
def bind(cls):
    cls.install_phase19 = install_phase19
    cls.install_phase20 = install_phase20
    cls.persist_expansion = persist_expansion
