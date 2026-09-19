"""Persist Phase 10 versioned regime definitions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from research_db.persist.ids import stable_id
from research_db.regime.engine import RegimeDefinitionRegistry

ROOT = Path(__file__).resolve().parents[2]
DDL = ROOT / "sql" / "010_phase10_sqlite_twin.sql"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def install_phase10(self) -> None:
    self.conn.executescript(DDL.read_text(encoding="utf-8"))
    self.conn.commit()


def persist_regime_definitions(self, registry: RegimeDefinitionRegistry | None = None) -> dict[str, int]:
    registry = registry or RegimeDefinitionRegistry()
    now = _now()
    with self.conn:
        self._upsert(
            "ops__schema_gate",
            {
                "id": stable_id("gate", "phase10"),
                "phase": "phase10",
                "approved": 1,
                "ingestion_enabled": 0,
                "notes": "Versioned regime definitions only",
                "created_at": now,
            },
        )
        for dfn in registry.definitions:
            self._upsert(
                "research__regime_definition",
                {
                    "id": stable_id("regdef", dfn["code"], dfn["version"]),
                    "code": dfn["code"],
                    "version": dfn["version"],
                    "family": dfn["family"],
                    "rules": json.dumps(dfn["rules"]),
                    "status": dfn["status"],
                    "created_at": now,
                },
            )
    return {"definitions": self._count("research__regime_definition")}


def bind(store_cls) -> None:
    store_cls.install_phase10 = install_phase10
    store_cls.persist_regime_definitions = persist_regime_definitions
