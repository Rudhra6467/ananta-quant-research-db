"""Persist Phase 6 hypothesis lifecycle and analogue definition."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from research_db.memory.engine import HypothesisEngine
from research_db.persist.ids import stable_id

ROOT = Path(__file__).resolve().parents[2]
PHASE6_DDL = ROOT / "sql" / "006_phase6_sqlite_twin.sql"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def install_phase6(self) -> None:
    self.conn.executescript(PHASE6_DDL.read_text(encoding="utf-8"))
    self.conn.commit()


def memory_as_of(self, as_of: str) -> dict[str, list]:
    markets = list(
        self.conn.execute(
            """SELECT event_time, knowledge_time, close, state_version
               FROM state__market_state_observation
               WHERE knowledge_time <= ?
               ORDER BY knowledge_time""",
            (as_of,),
        )
    )
    regimes = list(
        self.conn.execute(
            """SELECT event_time, knowledge_time, label, value, epistemic_status
               FROM state__regime_observation
               WHERE knowledge_time <= ?
               ORDER BY knowledge_time""",
            (as_of,),
        )
    )
    return {"market_states": markets, "regime_states": regimes}


def persist_hypotheses(self, engine: HypothesisEngine) -> dict[str, int]:
    now = _now()
    with self.conn:
        self._upsert(
            "ops__schema_gate",
            {
                "id": stable_id("gate", "phase6"),
                "phase": "phase6",
                "approved": 1,
                "ingestion_enabled": 0,
                "notes": "Fixture hypothesis lifecycle only",
                "created_at": now,
            },
        )
        for row in engine.hypotheses:
            hid = stable_id("hyp", row["code"])
            rel = self.ids[f"rel:{row['relationship']}"]
            self._upsert(
                "research__hypothesis",
                {
                    "id": hid,
                    "code": row["code"],
                    "relationship_id": rel,
                    "claim_kind": row["claim_kind"],
                    "version": row["version"],
                    "created_at": now,
                },
            )
        for ev in engine.status_events:
            hid = stable_id("hyp", ev["hypothesis"])
            eid = stable_id("hsev", ev["hypothesis"], ev["knowledge_time"], ev["status"])
            self.conn.execute(
                """INSERT OR IGNORE INTO research__hypothesis_status_event
                   (id, hypothesis_id, status, event_time, knowledge_time,
                    evidence_direction, note, created_at)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (
                    eid,
                    hid,
                    ev["status"],
                    ev["event_time"],
                    ev["knowledge_time"],
                    ev.get("evidence_direction"),
                    ev.get("note"),
                    now,
                ),
            )
        for link in engine.support_links:
            self.conn.execute(
                """INSERT OR IGNORE INTO research__hypothesis_support_link
                   (id, hypothesis_id, source_kind, source_id, event_time, knowledge_time, created_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (
                    stable_id("hsl", link["hypothesis"], link["source_kind"], link["source_id"]),
                    stable_id("hyp", link["hypothesis"]),
                    link["source_kind"],
                    link["source_id"],
                    link["event_time"],
                    link["knowledge_time"],
                    now,
                ),
            )
        for ad in engine.analogue_definitions:
            self._upsert(
                "research__analogue_definition",
                {
                    "id": stable_id("anadef", ad["code"]),
                    "code": ad["code"],
                    "version": ad["version"],
                    "metric_name": ad["metric_name"],
                    "description": ad["description"],
                    "created_at": now,
                },
            )
        self.conn.execute("DELETE FROM analytics__hypothesis_current_status")
        latest: dict[str, str] = {}
        times: dict[str, str] = {}
        for ev in engine.status_events:
            latest[ev["hypothesis"]] = ev["status"]
            times[ev["hypothesis"]] = ev["knowledge_time"]
        for code, status in latest.items():
            self.conn.execute(
                """INSERT INTO analytics__hypothesis_current_status
                   (hypothesis_id, status, knowledge_time, computed_at)
                   VALUES (?,?,?,?)""",
                (stable_id("hyp", code), status, times[code], now),
            )
    return {
        "hypotheses": self._count("research__hypothesis"),
        "status_events": self._count("research__hypothesis_status_event"),
        "support_links": self._count("research__hypothesis_support_link"),
        "analogues": self._count("research__analogue_definition"),
    }


def bind(store_cls) -> None:
    store_cls.install_phase6 = install_phase6
    store_cls.memory_as_of = memory_as_of
    store_cls.persist_hypotheses = persist_hypotheses
