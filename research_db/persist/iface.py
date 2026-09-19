from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from research_db.iface.engine import QueryCatalog
from research_db.persist.ids import stable_id
DDL = Path(__file__).resolve().parents[2] / "sql" / "016_phase16_sqlite_twin.sql"
def _now():
    return datetime.now(timezone.utc).isoformat()
def install_phase16(self):
    self.conn.executescript(DDL.read_text(encoding="utf-8")); self.conn.commit()
def persist_query_catalog(self, catalog=None):
    catalog = catalog or QueryCatalog()
    now = _now()
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate","phase16"),"phase":"phase16","approved":1,"ingestion_enabled":0,"notes":"Read-only catalog","created_at":now})
        for name in catalog.queries:
            self._upsert("interface__query_catalog", {"id": stable_id("qcat", name), "name": name, "mutation": 0})
    return {"queries": self._count("interface__query_catalog")}
def bind(cls):
    cls.install_phase16 = install_phase16
    cls.persist_query_catalog = persist_query_catalog
