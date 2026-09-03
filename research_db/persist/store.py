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
