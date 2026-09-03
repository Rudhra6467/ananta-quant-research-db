"""Persist Phase 4 request registry and rolling observation state."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from research_db.lifecycle.store import EmpiricalMemory
from research_db.observe.engine import ALLOWED, ObservationEngine, REQUESTED_PERIODS, signature_for
from research_db.persist.ids import stable_id

ROOT = Path(__file__).resolve().parents[2]
PHASE4_DDL = ROOT / "sql" / "004_phase4_sqlite_twin.sql"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def install_phase4(self) -> None:
    self.conn.executescript(PHASE4_DDL.read_text(encoding="utf-8"))
    self.conn.commit()


def persist_observation_engine(self, memory: EmpiricalMemory, engine: ObservationEngine) -> dict[str, int]:
    now = _now()
    with self.conn:
        self._upsert(
            "ops__schema_gate",
            {
                "id": stable_id("gate", "phase4"),
                "phase": "phase4",
                "approved": 1,
                "ingestion_enabled": 0,
                "notes": "Fixture observation engine only",
                "created_at": now,
            },
        )
        for period in REQUESTED_PERIODS:
            signature = signature_for(period)
            if signature not in ALLOWED:
                raise RuntimeError("refusing unrequested parameter set")
            pid = self.ids[f"ps:{signature}"]
            self._upsert(
                "research__feature_request",
                {
                    "id": stable_id("freq", signature),
                    "feature_version_id": self.ids["feature_version"],
                    "parameter_set_id": pid,
                    "signature": signature,
                    "status": "active",
                    "created_at": now,
                },
            )
            state = engine.states[signature]
            self.conn.execute("DELETE FROM ops__feature_roll_state WHERE parameter_set_id=?", (pid,))
            self.conn.execute(
                """INSERT INTO ops__feature_roll_state
                   (parameter_set_id, period, last_event_time, last_close, avg_gain, avg_loss,
                    primed, seed_closes, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    pid,
                    period,
                    state.last_event_time,
                    state.last_close,
                    state.avg_gain,
                    state.avg_loss,
                    1 if state.primed else 0,
                    json.dumps(state.seed_closes[-state.period - 1 :]),
                    now,
                ),
            )
            if state.last_event_time:
                self.conn.execute("DELETE FROM ops__observation_watermark WHERE parameter_set_id=?", (pid,))
                count = sum(1 for row in engine.observations if row["parameter_set"] == signature)
                self.conn.execute(
                    """INSERT INTO ops__observation_watermark
                       (parameter_set_id, last_event_time, last_count, updated_at)
                       VALUES (?,?,?,?)""",
                    (pid, state.last_event_time, count, now),
                )
        existing = {
            (row["parameter_set_id"], row["event_time"])
            for row in self.conn.execute("SELECT parameter_set_id, event_time FROM feature__observation")
        }
        inserted = 0
        for obs in engine.observations:
            pid = self.ids[f"ps:{obs['parameter_set']}"]
            key = (pid, obs["event_time"])
            if key in existing:
                continue
            self.conn.execute(
                """INSERT INTO feature__observation
                   (id, feature_version_id, parameter_set_id, instrument_id, timeframe_id,
                    dataset_snapshot_id, event_time, knowledge_time, value, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    stable_id("obs4", obs["parameter_set"], obs["event_time"]),
                    self.ids["feature_version"],
                    pid,
                    self.ids["instrument"],
                    self.ids["tf"],
                    self.ids["snapshot"],
                    obs["event_time"],
                    obs["as_of_time"],
                    obs["value"],
                    now,
                ),
            )
            existing.add(key)
            inserted += 1
    return {
        "requests": self._count("research__feature_request"),
        "roll_states": self._count("ops__feature_roll_state"),
        "engine_observations": len(engine.observations),
        "inserted_observations": inserted,
    }


def bind(store_cls) -> None:
    store_cls.install_phase4 = install_phase4
    store_cls.persist_observation_engine = persist_observation_engine
