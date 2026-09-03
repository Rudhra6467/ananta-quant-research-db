"""Phase 2 fixture persistence. Product store is PostgreSQL 16 + TimescaleDB."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from research_db.lifecycle.engine import requested_parameter_sets, run_fixture_lifecycle
from research_db.lifecycle.store import EmpiricalMemory
from research_db.persist.ids import request_hash, stable_id
from research_db.persist import evidence as phase3_evidence

ROOT = Path(__file__).resolve().parents[2]
SQLITE_DDL = ROOT / "sql" / "002_phase2_sqlite_twin.sql"
LIVE_TABLES = {
    "ops__current_market_state", "ops__current_feature_value",
    "ops__current_regime_state", "ops__operational_relationship_applicability",
}
FORBIDDEN_LIVE = ("raw__", "market__", "feature__", "research__relationship_evidence", "research__ranking")


class LiveQueryDenied(PermissionError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def open_fixture_store(path: str | Path = ":memory:") -> "FixtureStore":
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = FULL")
    store = FixtureStore(conn)
    store.install_schema()
    return store


def open_evidence_store(path: str | Path = ":memory:") -> "FixtureStore":
    store = open_fixture_store(path)
    store.install_phase3()
    return store


class FixtureStore:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self._live = False
        self.ids: dict[str, str] = {}

    def install_schema(self) -> None:
        self.conn.executescript(SQLITE_DDL.read_text(encoding="utf-8"))
        self.conn.commit()

    def execute(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Cursor:
        if self._live:
            lowered = sql.lower()
            if not lowered.lstrip().startswith("select"):
                raise LiveQueryDenied("live path is read-only")
            if any(token in lowered for token in FORBIDDEN_LIVE):
                raise LiveQueryDenied(f"live path may not read research history: {sql}")
            if not any(table in lowered for table in LIVE_TABLES):
                raise LiveQueryDenied(f"live path limited to ops current projections: {sql}")
        return self.conn.execute(sql, tuple(params))

    def live(self) -> "FixtureStore":
        child = FixtureStore(self.conn)
        child.ids = self.ids
        child._live = True
        return child

    def persist_memory(self, memory: EmpiricalMemory | None = None) -> dict[str, int]:
        memory = memory or run_fixture_lifecycle()
        with self.conn:
            self._persist_identities(memory)
            self._persist_definitions(memory)
            self._persist_runs(memory)
            raw_n = self._persist_raw_and_bars(memory)
            obs_n = self._persist_observations(memory)
            self._persist_projections(memory)
            self._assert_gate()
        return {"canonical_bars": raw_n, "observations": obs_n, "parameter_sets": self._count("research__parameter_set")}

    def persist_incremental(self, memory: EmpiricalMemory) -> dict[str, int]:
        before_bars = self._count("market__ohlcv_bar")
        before_obs = self._count("feature__observation")
        with self.conn:
            self._persist_runs(memory)
            raw_n = self._persist_raw_and_bars(memory)
            obs_n = self._persist_observations(memory)
            self._persist_projections(memory)
        return {
            "new_bars": self._count("market__ohlcv_bar") - before_bars,
            "new_observations": self._count("feature__observation") - before_obs,
            "inserted_bars_this_call": raw_n,
            "inserted_obs_this_call": obs_n,
        }

    def _count(self, table: str) -> int:
        return int(self.conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"])

    def _upsert(self, table: str, cols: dict[str, Any]) -> None:
        keys = list(cols)
        sql = f"INSERT OR IGNORE INTO {table} ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)})"
        self.conn.execute(sql, [cols[k] for k in keys])

    def _persist_identities(self, memory: EmpiricalMemory) -> None:
        now = _now()
        self.ids.update({
            "source": stable_id("source", "synthetic_fixture"),
            "venue": stable_id("venue", "FIXTURE"),
            "btc": stable_id("asset", "BTC"),
            "usd": stable_id("asset", "USD"),
            "tf": stable_id("timeframe", "1h"),
            "instrument": stable_id("instrument", "FIXTURE", "BTC-USD-SPOT", "spot"),
            "snapshot": stable_id("snapshot", "fixture-btc-1h-v1"),
        })
        self._upsert("ref__data_source", {"id": self.ids["source"], "code": "synthetic_fixture", "name": "Synthetic fixture", "created_at": now})
        self._upsert("ref__venue", {"id": self.ids["venue"], "code": "FIXTURE", "name": "Fixture venue", "created_at": now})
        self._upsert("ref__asset", {"id": self.ids["btc"], "symbol": "BTC", "name": "Bitcoin", "asset_class": "crypto", "created_at": now})
        self._upsert("ref__asset", {"id": self.ids["usd"], "symbol": "USD", "name": "US Dollar", "asset_class": "fiat", "created_at": now})
        self._upsert("ref__timeframe", {"id": self.ids["tf"], "code": "1h", "seconds": 3600, "created_at": now})
        self._upsert("ref__instrument", {"id": self.ids["instrument"], "venue_id": self.ids["venue"], "base_asset_id": self.ids["btc"], "quote_asset_id": self.ids["usd"], "symbol": "BTC-USD-SPOT", "kind": "spot", "created_at": now})
        self._upsert("ops__dataset_snapshot", {"id": self.ids["snapshot"], "code": "fixture-btc-1h-v1", "data_source_id": self.ids["source"], "as_of_time": memory.dataset_snapshots[0]["as_of_time"], "notes": "Phase 2 synthetic fixture. Not exchange history.", "created_at": now})
        self._upsert("ops__schema_gate", {"id": stable_id("gate", "phase2"), "phase": "phase2", "approved": 1, "ingestion_enabled": 0, "notes": "Fixture persistence only", "created_at": now})

    def _persist_definitions(self, memory: EmpiricalMemory) -> None:
        now = _now()
        self.ids["indicator"] = stable_id("indicator", "RSI")
        self.ids["feature"] = stable_id("feature", "RSI")
        self.ids["feature_version"] = stable_id("feature_version", "RSI", "v1")
        self._upsert("research__indicator_definition", {"id": self.ids["indicator"], "family_code": "RSI", "name": "Relative Strength Index", "created_at": now})
        self._upsert("research__feature_definition", {"id": self.ids["feature"], "indicator_id": self.ids["indicator"], "code": "RSI", "name": "RSI", "created_at": now})
        self._upsert("research__feature_version", {"id": self.ids["feature_version"], "feature_id": self.ids["feature"], "version": "v1", "formula_ref": "wilder-rsi", "created_at": now})
        self._upsert("research__parameter_definition", {"id": stable_id("paramdef", "RSI", "period"), "feature_id": self.ids["feature"], "name": "period", "topology": "ordered_discrete", "domain": json.dumps({"min": 2, "max": 50}), "created_at": now})
        for key, spec in memory.parameter_sets.items():
            pid = stable_id("paramset", key)
            self.ids[f"ps:{key}"] = pid
            self._upsert("research__parameter_set", {"id": pid, "feature_version_id": self.ids["feature_version"], "signature": key, "param_values": json.dumps({"period": spec["period"]}), "created_at": now})
        region = memory.parameter_regions["RSI(12-17)"]
        rid = stable_id("region", "RSI(12-17)")
        self.ids["region"] = rid
        self._upsert("research__parameter_region", {"id": rid, "feature_id": self.ids["feature"], "code": "RSI(12-17)", "dimension": region["dimension"], "lo": region["lo"], "hi": region["hi"], "detection": region["detection"], "created_at": now})
        for member in region["members"]:
            self._upsert("research__parameter_region_member", {"region_id": rid, "parameter_set_id": self.ids[f"ps:{member}"]})
        outcome_id = stable_id("outcome", "future_return_4")
        self._upsert("research__outcome_definition", {"id": outcome_id, "code": "future_return_4h", "horizon_bars": 4, "description": "4-bar forward simple return", "created_at": now})
        for code, rel in memory.relationship_definitions.items():
            rel_id = stable_id("rel", code)
            self.ids[f"rel:{code}"] = rel_id
            spec = {"code": code, "antecedent": rel["antecedent"], "outcome": rel["outcome"], "context": rel["context"]}
            self._upsert("research__relationship_definition", {"id": rel_id, "code": code, "version": rel["version"], "outcome_id": outcome_id, "expression": json.dumps(spec), "created_at": now})
            self._upsert("research__combination_request", {"id": stable_id("combo", code), "code": code, "relationship_id": rel_id, "request_hash": request_hash(spec), "specification": json.dumps(spec), "created_at": now})

    def _persist_runs(self, memory: EmpiricalMemory) -> None:
        now = _now()
        ingest = memory.ingestion_runs[0]
        canon = memory.canonicalization_runs[0]
        self.ids["ingest"] = stable_id("ingest", ingest["id"])
        self.ids["canon"] = stable_id("canon", canon["id"])
        self._upsert("ops__ingestion_run", {"id": self.ids["ingest"], "dataset_snapshot_id": self.ids["snapshot"], "status": ingest["status"], "started_at": now, "finished_at": now, "config": json.dumps({"fixture": True, "exchange": False}), "created_at": now})
        self._upsert("ops__canonicalization_run", {"id": self.ids["canon"], "ingestion_run_id": self.ids["ingest"], "version": canon["version"], "status": canon["status"], "created_at": now})
        if len(memory.ingestion_runs) > 1:
            inc = memory.ingestion_runs[-1]
            self.ids["ingest_inc"] = stable_id("ingest", inc["id"])
            self.ids["canon_inc"] = stable_id("canon", memory.canonicalization_runs[-1]["id"])
            self._upsert("ops__ingestion_run", {"id": self.ids["ingest_inc"], "dataset_snapshot_id": self.ids["snapshot"], "status": inc["status"], "started_at": now, "finished_at": now, "config": json.dumps({"fixture": True, "increment": True}), "created_at": now})
            self._upsert("ops__canonicalization_run", {"id": self.ids["canon_inc"], "ingestion_run_id": self.ids["ingest_inc"], "version": memory.canonicalization_runs[-1]["version"], "status": memory.canonicalization_runs[-1]["status"], "created_at": now})

    def _persist_raw_and_bars(self, memory: EmpiricalMemory) -> int:
        now = _now()
        inserted = 0
        ingest_by_n = self.ids["ingest"]
        canon_id = self.ids["canon"]
        known_raw = {row["source_record_id"] for row in self.conn.execute("SELECT source_record_id FROM raw__market_event")}
        for raw in memory.raw_events:
            if raw["source_record_id"] in known_raw:
                continue
            run_id, c_id = ingest_by_n, canon_id
            if len(memory.raw_events) > 48 and raw is memory.raw_events[-1] and "ingest_inc" in self.ids:
                run_id, c_id = self.ids["ingest_inc"], self.ids["canon_inc"]
            rid = stable_id("raw", raw["source_record_id"])
            bid = stable_id("bar", raw["source_record_id"])
            knowledge_time = next(b["as_of_time"] for b in memory.canonical_bars if b["source_record_id"] == raw["source_record_id"])
            self.conn.execute("INSERT INTO raw__market_event (id, data_source_id, source_record_id, instrument_id, timeframe_id, dataset_snapshot_id, ingestion_run_id, event_time, knowledge_time, payload, checksum, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (rid, self.ids["source"], raw["source_record_id"], self.ids["instrument"], self.ids["tf"], self.ids["snapshot"], run_id, raw["event_time"], knowledge_time, json.dumps(raw["payload"]), raw["checksum"], now))
            bar = next(b for b in memory.canonical_bars if b["source_record_id"] == raw["source_record_id"])
            self.conn.execute("INSERT INTO market__ohlcv_bar (id, instrument_id, venue_id, timeframe_id, dataset_snapshot_id, raw_event_id, canonicalization_run_id, event_time, knowledge_time, open, high, low, close, volume, canonicalization_version, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (bid, self.ids["instrument"], self.ids["venue"], self.ids["tf"], self.ids["snapshot"], rid, c_id, bar["event_time"], bar["as_of_time"], bar["open"], bar["high"], bar["low"], bar["close"], bar["volume"], bar["canonicalization_version"], now))
            inserted += 1
            known_raw.add(raw["source_record_id"])
        if memory.canonical_bars:
            last = memory.canonical_bars[-1]
            self._upsert("ops__persist_watermark", {"stream": "fixture-btc-1h-v1", "last_event_time": last["event_time"], "last_source_record_id": last["source_record_id"], "updated_at": now})
            self.conn.execute("UPDATE ops__persist_watermark SET last_event_time=?, last_source_record_id=?, updated_at=? WHERE stream=?", (last["event_time"], last["source_record_id"], now, "fixture-btc-1h-v1"))
        return inserted

    def _persist_observations(self, memory: EmpiricalMemory) -> int:
        now = _now()
        existing = {(row["parameter_set_id"], row["event_time"]) for row in self.conn.execute("SELECT parameter_set_id, event_time FROM feature__observation")}
        inserted = 0
        allowed = set(requested_parameter_sets())
        for obs in memory.feature_observations:
            if obs["parameter_set"] not in allowed:
                raise RuntimeError("refusing unrequested parameter set")
            pid = self.ids[f"ps:{obs['parameter_set']}"]
            key = (pid, obs["event_time"])
            if key in existing:
                continue
            self.conn.execute("INSERT INTO feature__observation (id, feature_version_id, parameter_set_id, instrument_id, timeframe_id, dataset_snapshot_id, event_time, knowledge_time, value, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)", (stable_id("obs", obs["parameter_set"], obs["event_time"]), self.ids["feature_version"], pid, self.ids["instrument"], self.ids["tf"], self.ids["snapshot"], obs["event_time"], obs["as_of_time"], obs["value"], now))
            existing.add(key)
            inserted += 1
        return inserted

    def _persist_projections(self, memory: EmpiricalMemory) -> None:
        now = _now()
        state = next(iter(memory.current_market_state.values()))
        self.conn.execute("DELETE FROM ops__current_market_state")
        self.conn.execute("INSERT INTO ops__current_market_state (id, instrument_id, venue_id, timeframe_id, event_time, as_of_time, state_version, payload, updated_at) VALUES (?,?,?,?,?,?,?,?,?)", (stable_id("cms", "BTC-USD-SPOT", "1h"), self.ids["instrument"], self.ids["venue"], self.ids["tf"], state["event_time"], state["as_of_time"], state["state_version"], json.dumps({"close": state["close"]}), now))
        self.conn.execute("DELETE FROM ops__current_feature_value")
        for key, row in memory.current_feature_value.items():
            self.conn.execute("INSERT INTO ops__current_feature_value (id, feature_version_id, parameter_set_id, instrument_id, timeframe_id, event_time, as_of_time, value, updated_at) VALUES (?,?,?,?,?,?,?,?,?)", (stable_id("cfv", key), self.ids["feature_version"], self.ids[f"ps:{key}"], self.ids["instrument"], self.ids["tf"], row["event_time"], row["as_of_time"], row["value"], now))
        regime = next(iter(memory.current_regime_state.values()))
        self.conn.execute("DELETE FROM ops__current_regime_state")
        self.conn.execute("INSERT INTO ops__current_regime_state (id, instrument_id, timeframe_id, regime_family, label, event_time, as_of_time, provenance, updated_at) VALUES (?,?,?,?,?,?,?,?,?)", (stable_id("crs", "rsi_region"), self.ids["instrument"], self.ids["tf"], regime["regime_family"], regime["label"], regime["event_time"], regime["as_of_time"], json.dumps(regime["provenance"] if isinstance(regime["provenance"], dict) else {"source": regime["provenance"]}), now))
        self.conn.execute("DELETE FROM ops__operational_relationship_applicability")
        for code, row in memory.operational_applicability.items():
            self.conn.execute("INSERT INTO ops__operational_relationship_applicability (id, relationship_code, instrument_id, timeframe_id, regime_bucket, active, score, state_version, updated_at) VALUES (?,?,?,?,?,?,?,?,?)", (stable_id("ora", code), code, self.ids["instrument"], self.ids["tf"], row.get("regime_bucket"), 1 if row["active"] else 0, row.get("score"), row["state_version"], now))

    def _assert_gate(self) -> None:
        row = self.conn.execute("SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='phase2'").fetchone()
        if row is None or int(row["ingestion_enabled"]) != 0:
            raise RuntimeError("phase2 gate must keep ingestion_enabled=false")

    def bars_as_of(self, as_of: str) -> list[sqlite3.Row]:
        return list(self.conn.execute("SELECT event_time, close, knowledge_time, raw_event_id FROM market__ohlcv_bar WHERE event_time <= ? AND knowledge_time <= ? ORDER BY event_time", (as_of, as_of)))


phase3_evidence.bind(FixtureStore)
