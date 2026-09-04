from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from research_db.persist.ids import stable_id
from research_db.security.engine import AccessPolicy
DDL = Path(__file__).resolve().parents[2] / "sql" / "015_phase15_sqlite_twin.sql"
def _now():
    return datetime.now(timezone.utc).isoformat()
def install_phase15(self):
    self.conn.executescript(DDL.read_text(encoding="utf-8")); self.conn.commit()
def persist_access_policy(self, policy=None):
    policy = policy or AccessPolicy()
    now = _now()
    with self.conn:
        self._upsert("ops__schema_gate", {"id": stable_id("gate","phase15"),"phase":"phase15","approved":1,"ingestion_enabled":0,"notes":"Access policy","created_at":now})
        for i, g in enumerate(policy.grants):
            self._upsert("ops__access_grant", {"id": stable_id("ag", g["role"], g["surface"], g["action"], str(i)), "role": g["role"], "surface": g["surface"], "action": g["action"]})
        for i, f in enumerate(policy.forbidden):
            self._upsert("ops__access_forbid", {"id": stable_id("af", f["role"], f["surface"], f["action"], str(i)), "role": f["role"], "surface": f["surface"], "action": f["action"]})
    return {"grants": self._count("ops__access_grant"), "forbids": self._count("ops__access_forbid")}
def bind(cls):
    cls.install_phase15 = install_phase15
    cls.persist_access_policy = persist_access_policy
