"""Persist Phase 5 current state / regime projections."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from research_db.persist.ids import stable_id
from research_db.state.engine import REGIME_FAMILY, StateCompiler

ROOT = Path(__file__).resolve().parents[2]
PHASE5_DDL = ROOT / "sql" / "005_phase5_sqlite_twin.sql"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def install_phase5(self) -> None:
    self.conn.executescript(PHASE5_DDL.read_text(encoding="utf-8"))
    self.conn.commit()


def persist_state_compiler(self, compiler: StateCompiler) -> dict[str, int]:
    now = _now()
    market = compiler.current_market()
    regime = compiler.current_regime()
    with self.conn:
        self._upsert(
            "ops__schema_gate",
            {
                "id": stable_id("gate", "phase5"),
                "phase": "phase5",
                "approved": 1,
                "ingestion_enabled": 0,
                "notes": "Fixture current-state compiler only",
                "created_at": now,
            },
        )
        self._upsert(
            "state__regime_family",
            {
                "id": stable_id("rfam", REGIME_FAMILY),
                "code": REGIME_FAMILY,
                "description": "Median RSI(12-17) vs oversold threshold",
                "created_at": now,
            },
        )
        mid = stable_id("sms", market["event_time"])
        self.conn.execute(
            """INSERT OR IGNORE INTO state__market_state_observation
               (id, instrument_id, venue_id, timeframe_id, event_time, knowledge_time,
                close, state_version, created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                mid,
                self.ids["instrument"],
                self.ids["venue"],
                self.ids["tf"],
                market["event_time"],
                market["as_of_time"],
                market["close"],
                market["state_version"],
                now,
            ),
        )
        rid = stable_id("sro", regime["event_time"], REGIME_FAMILY)
        self.conn.execute(
            """INSERT OR IGNORE INTO state__regime_observation
               (id, instrument_id, timeframe_id, regime_family, label, value,
                epistemic_status, event_time, knowledge_time, provenance, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                rid,
                self.ids["instrument"],
                self.ids["tf"],
                regime["regime_family"],
                regime["label"],
                regime["value"],
                regime["epistemic_status"],
                regime["event_time"],
                regime["as_of_time"],
                json.dumps(
                    {
                        "source": regime["provenance"],
                        "threshold": regime["threshold"],
                        "n_features": regime["n_features"],
                    }
                ),
                now,
            ),
        )
        self.conn.execute("DELETE FROM ops__current_market_state")
        self.conn.execute(
            """INSERT INTO ops__current_market_state
               (id, instrument_id, venue_id, timeframe_id, event_time, as_of_time,
                state_version, payload, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                stable_id("cms", "BTC-USD-SPOT", "1h"),
                self.ids["instrument"],
                self.ids["venue"],
                self.ids["tf"],
                market["event_time"],
                market["as_of_time"],
                market["state_version"],
                json.dumps({"close": market["close"]}),
                now,
            ),
        )
        self.conn.execute("DELETE FROM ops__current_feature_value")
        for key, row in compiler.feature_currents.items():
            pid = self.ids[f"ps:{key}"]
            self.conn.execute(
                """INSERT INTO ops__current_feature_value
                   (id, feature_version_id, parameter_set_id, instrument_id, timeframe_id,
                    event_time, as_of_time, value, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    stable_id("cfv", key),
                    self.ids["feature_version"],
                    pid,
                    self.ids["instrument"],
                    self.ids["tf"],
                    row["event_time"],
                    row["as_of_time"],
                    row["value"],
                    now,
                ),
            )
        self.conn.execute("DELETE FROM ops__current_regime_state")
        self.conn.execute(
            """INSERT INTO ops__current_regime_state
               (id, instrument_id, timeframe_id, regime_family, label, event_time,
                as_of_time, provenance, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                stable_id("crs", REGIME_FAMILY),
                self.ids["instrument"],
                self.ids["tf"],
                regime["regime_family"],
                regime["label"],
                regime["event_time"],
                regime["as_of_time"],
                json.dumps(
                    {
                        "source": regime["provenance"],
                        "value": regime["value"],
                        "epistemic_status": regime["epistemic_status"],
                        "threshold": regime["threshold"],
                    }
                ),
                now,
            ),
        )
        self.conn.execute("DELETE FROM ops__state_compile_watermark")
        self.conn.execute(
            """INSERT INTO ops__state_compile_watermark
               (id, last_event_time, last_regime_label, updated_at)
               VALUES (?,?,?,?)""",
            ("fixture-btc-1h", market["event_time"], regime["label"], now),
        )
    return {
        "market_facts": self._count("state__market_state_observation"),
        "regime_facts": self._count("state__regime_observation"),
        "current_features": self._count("ops__current_feature_value"),
    }


def bind(store_cls) -> None:
    store_cls.install_phase5 = install_phase5
    store_cls.persist_state_compiler = persist_state_compiler
