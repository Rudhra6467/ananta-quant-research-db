"""Persist Phase 9 requested analytical observations into feature.observation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from research_db.analyze.engine import AnalyticalEngine
from research_db.persist.ids import stable_id


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def install_phase9(self) -> None:
    self._upsert(
        "ops__schema_gate",
        {
            "id": stable_id("gate", "phase9"),
            "phase": "phase9",
            "approved": 1,
            "ingestion_enabled": 0,
            "notes": "Requested RET(1) and RANGE_VOL(1) only",
            "created_at": _now(),
        },
    )
    self.conn.commit()


def persist_analytical(self, engine: AnalyticalEngine) -> dict[str, int]:
    now = _now()
    with self.conn:
        install_phase9(self)
        for sig in engine.requests:
            family = sig.split("(")[0]
            ind = stable_id("indicator", family)
            feat = stable_id("feature", family)
            ver = stable_id("feature_version", family, "v1")
            ps = stable_id("paramset", sig)
            self._upsert("research__indicator_definition", {"id": ind, "family_code": family, "name": family, "created_at": now})
            self._upsert("research__feature_definition", {"id": feat, "indicator_id": ind, "code": family, "name": family, "created_at": now})
            self._upsert("research__feature_version", {"id": ver, "feature_id": feat, "version": "v1", "formula_ref": sig, "created_at": now})
            self._upsert("research__parameter_set", {"id": ps, "feature_version_id": ver, "signature": sig, "param_values": json.dumps({"window": 1}), "created_at": now})
            self._upsert("research__feature_request", {"id": stable_id("freq", sig), "feature_version_id": ver, "parameter_set_id": ps, "signature": sig, "status": "active", "created_at": now})
            self.ids[f"ps:{sig}"] = ps
            self.ids[f"fv:{family}"] = ver
        for row in engine.observations:
            oid = stable_id("aobs", row["parameter_set"], row["event_time"])
            self.conn.execute(
                """INSERT OR IGNORE INTO feature__observation
                   (id, feature_version_id, parameter_set_id, instrument_id, timeframe_id,
                    dataset_snapshot_id, event_time, knowledge_time, value, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    oid,
                    self.ids[f"fv:{row['feature']}"],
                    self.ids[f"ps:{row['parameter_set']}"],
                    self.ids["instrument"],
                    self.ids["tf"],
                    self.ids["snapshot"],
                    row["event_time"],
                    row["as_of_time"],
                    row["value"],
                    now,
                ),
            )
    return {"analytical_observations": len(engine.observations), "requests": len(engine.requests)}


def bind(store_cls) -> None:
    store_cls.install_phase9 = install_phase9
    store_cls.persist_analytical = persist_analytical
