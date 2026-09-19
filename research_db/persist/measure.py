"""Persist Phase 7 requested measurement facts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from research_db.measure.engine import MeasurementEngine
from research_db.persist.ids import stable_id

ROOT = Path(__file__).resolve().parents[2]
PHASE7_DDL = ROOT / "sql" / "007_phase7_sqlite_twin.sql"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def install_phase7(self) -> None:
    self.conn.executescript(PHASE7_DDL.read_text(encoding="utf-8"))
    self.conn.commit()


def persist_measurements(self, engine: MeasurementEngine) -> dict[str, int]:
    now = _now()
    with self.conn:
        self._upsert(
            "ops__schema_gate",
            {
                "id": stable_id("gate", "phase7"),
                "phase": "phase7",
                "approved": 1,
                "ingestion_enabled": 0,
                "notes": "Fixture measurement representation only",
                "created_at": now,
            },
        )
        for fam in engine.families:
            self._upsert(
                "research__measurement_family",
                {
                    "id": stable_id("mfam", fam["code"]),
                    "code": fam["code"],
                    "description": fam["description"],
                    "created_at": now,
                },
            )
        for dfn in engine.definitions:
            self._upsert(
                "research__measurement_definition",
                {
                    "id": stable_id("mdfn", dfn["code"]),
                    "code": dfn["code"],
                    "family_id": stable_id("mfam", dfn["family"]),
                    "param_schema": json.dumps(dfn["param_schema"]),
                    "created_at": now,
                },
            )
        for req in engine.requests:
            self._upsert(
                "research__measurement_request",
                {
                    "id": stable_id("mreq", req),
                    "definition_id": stable_id("mdfn", req),
                    "code": req,
                    "status": "active",
                    "created_at": now,
                },
            )
        for obs in engine.observations:
            oid = stable_id("mobs", obs["definition"], obs["relationship"], obs["knowledge_time"])
            rel_id = self.ids.get(f"rel:{obs['relationship']}")
            hyp_id = stable_id("hyp", obs["hypothesis"]) if obs.get("hypothesis") else None
            self.conn.execute(
                """INSERT OR IGNORE INTO research__measurement_observation
                   (id, definition_id, relationship_id, hypothesis_id, experiment_run_id,
                    dataset_snapshot_id, point_value, sample_size, epistemic_status,
                    evidence_direction, condition_digest, event_time, knowledge_time,
                    payload, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    oid,
                    stable_id("mdfn", obs["definition"]),
                    rel_id,
                    hyp_id,
                    self.ids.get("exprun"),
                    self.ids.get("snapshot"),
                    obs.get("point_value"),
                    obs.get("sample_size"),
                    obs["epistemic_status"],
                    obs.get("evidence_direction"),
                    obs["condition_digest"],
                    obs["event_time"],
                    obs["knowledge_time"],
                    json.dumps(obs.get("conditions") or {}),
                    now,
                ),
            )
        for dist in engine.distributions:
            parent = stable_id("mobs", dist["definition"], dist["relationship"], dist["knowledge_time"])
            self.conn.execute(
                """INSERT OR IGNORE INTO research__measurement_distribution
                   (id, measurement_observation_id, representation, payload, created_at)
                   VALUES (?,?,?,?,?)""",
                (
                    stable_id("mdist", parent, dist["representation"]),
                    parent,
                    dist["representation"],
                    json.dumps(dist["payload"]),
                    now,
                ),
            )
        self.conn.execute("DELETE FROM analytics__measurement_current")
        latest = {}
        for obs in engine.observations:
            key = (obs["definition"], obs["relationship"], obs["condition_digest"])
            latest[key] = obs
        for (defn, rel, digest), obs in latest.items():
            self.conn.execute(
                """INSERT INTO analytics__measurement_current
                   (definition_id, relationship_id, condition_digest, point_value,
                    epistemic_status, knowledge_time, computed_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (
                    stable_id("mdfn", defn),
                    self.ids.get(f"rel:{rel}"),
                    digest,
                    obs.get("point_value"),
                    obs["epistemic_status"],
                    obs["knowledge_time"],
                    now,
                ),
            )
    return {
        "requests": self._count("research__measurement_request"),
        "observations": self._count("research__measurement_observation"),
        "distributions": self._count("research__measurement_distribution"),
    }


def bind(store_cls) -> None:
    store_cls.install_phase7 = install_phase7
    store_cls.persist_measurements = persist_measurements
