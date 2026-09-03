"""Phase 3 fixture evidence persistence. Not ranking. Not ingest."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from research_db.lifecycle.store import EmpiricalMemory
from research_db.persist.ids import stable_id

ROOT = Path(__file__).resolve().parents[2]
PHASE3_DDL = ROOT / "sql" / "003_phase3_sqlite_twin.sql"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def install_phase3(self) -> None:
    self.conn.executescript(PHASE3_DDL.read_text(encoding="utf-8"))
    self.conn.commit()


def persist_evidence(self, memory: EmpiricalMemory) -> dict[str, int]:
    if _count_optional(self, "research__relationship_evidence") < 0:
        raise RuntimeError("phase3 schema not installed")
    with self.conn:
        _seed_validation_stages(self)
        _persist_experiment_runs(self, memory)
        _persist_trials_and_evidence(self, memory)
        persist_current_summaries(self, memory)
        _assert_phase3_gate(self)
    return {
        "experiment_runs": self._count("research__experiment_run"),
        "trials": self._count("research__experiment_trial"),
        "evidence": self._count("research__relationship_evidence"),
    }


def persist_reset_cohort(self, memory: EmpiricalMemory, code: str) -> str:
    now = _now()
    run_id = stable_id("exprun", code)
    with self.conn:
        self._upsert(
            "research__experiment_run",
            {
                "id": run_id,
                "code": code,
                "dataset_snapshot_id": self.ids["snapshot"],
                "code_commit": "phase3-reset-cohort",
                "config_hash": "reset",
                "status": "planned",
                "created_at": now,
            },
        )
    return run_id


def append_forward_evidence(self, memory: EmpiricalMemory, code: str, stage: str = "FORWARD") -> None:
    from research_db.lifecycle.engine import evaluate_relationship

    bars = memory.canonical_bars
    evaluate_relationship(memory, code, bars, stage, max(0, len(bars) - 12), len(bars))
    with self.conn:
        _seed_validation_stages(self)
        _persist_experiment_runs(self, memory)
        _persist_trials_and_evidence(self, memory)


def evidence_as_of(self, as_of: str):
    return list(
        self.conn.execute(
            """SELECT e.direction, e.effect, e.knowledge_time, r.code AS relationship, s.code AS stage
               FROM research__relationship_evidence e
               JOIN research__relationship_definition r ON r.id = e.relationship_id
               JOIN research__validation_stage s ON s.id = e.validation_stage_id
               WHERE e.knowledge_time <= ?
               ORDER BY e.knowledge_time, r.code""",
            (as_of,),
        )
    )


def persist_current_summaries(self, memory: EmpiricalMemory) -> None:
    now = _now()
    self.conn.execute("DELETE FROM analytics__relationship_current_summary")
    for code, row in memory.relationship_current_summary.items():
        self.conn.execute(
            """INSERT INTO analytics__relationship_current_summary
               (relationship_id, status, blended_score, historical_effect, oos_effect,
                scoring_model_version, source_watermark, computed_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                self.ids[f"rel:{code}"],
                row["status"],
                row.get("blended_score"),
                row.get("historical_effect"),
                row.get("oos_effect"),
                row["scoring_model_version"],
                row.get("source_watermark"),
                now,
            ),
        )


def bind(store_cls) -> None:
    store_cls.install_phase3 = install_phase3
    store_cls.persist_evidence = persist_evidence
    store_cls.persist_reset_cohort = persist_reset_cohort
    store_cls.append_forward_evidence = append_forward_evidence
    store_cls.evidence_as_of = evidence_as_of
    store_cls._persist_current_summaries = persist_current_summaries


def _count_optional(self, table: str) -> int:
    row = self.conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    if row is None:
        return -1
    return self._count(table)


def _seed_validation_stages(self) -> None:
    now = _now()
    for order, code in enumerate(("HISTORICAL", "OOS", "FORWARD", "PAPER", "CURRENT"), start=1):
        sid = stable_id("stage", code)
        self.ids[f"stage:{code}"] = sid
        self._upsert(
            "research__validation_stage",
            {"id": sid, "code": code, "sort_order": order, "created_at": now},
        )


def _persist_experiment_runs(self, memory: EmpiricalMemory) -> None:
    now = _now()
    if not memory.experiment_runs:
        return
    run = memory.experiment_runs[0]
    rid = stable_id("exprun", run["id"])
    self.ids["exprun"] = rid
    self._upsert(
        "research__experiment_run",
        {
            "id": rid,
            "code": run["id"],
            "dataset_snapshot_id": self.ids["snapshot"],
            "code_commit": run.get("code_commit"),
            "config_hash": "fixture-rsi-region",
            "status": run.get("status", "complete"),
            "created_at": now,
        },
    )
    self._upsert(
        "ops__schema_gate",
        {
            "id": stable_id("gate", "phase3"),
            "phase": "phase3",
            "approved": 1,
            "ingestion_enabled": 0,
            "notes": "Fixture evidence only",
            "created_at": now,
        },
    )


def _persist_trials_and_evidence(self, memory: EmpiricalMemory) -> None:
    now = _now()
    run_id = self.ids["exprun"]
    by_trial = {row["id"]: row for row in memory.experiment_trials}
    existing_trials = {row["id"] for row in self.conn.execute("SELECT id FROM research__experiment_trial")}
    existing_evidence = {
        row["trial_id"] for row in self.conn.execute("SELECT trial_id FROM research__relationship_evidence")
    }
    for ev in memory.evidence:
        trial = by_trial[ev["trial"]]
        stage = ev["stage"]
        trial_id = stable_id("trial", trial["id"])
        rel_id = self.ids[f"rel:{ev['relationship']}"]
        stage_id = self.ids[f"stage:{stage}"]
        if trial_id not in existing_trials:
            window = trial.get("window") or (None, None)
            self.conn.execute(
                """INSERT INTO research__experiment_trial
                   (id, experiment_run_id, relationship_id, instrument_id, timeframe_id,
                    validation_stage_id, status, skip_reason, window_start, window_end, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    trial_id,
                    run_id,
                    rel_id,
                    self.ids["instrument"],
                    self.ids["tf"],
                    stage_id,
                    trial.get("status", "complete"),
                    None,
                    window[0],
                    window[1],
                    now,
                ),
            )
            existing_trials.add(trial_id)
        if trial_id in existing_evidence:
            continue
        knowledge_time = memory.canonical_bars[-1]["as_of_time"]
        if stage == "HISTORICAL":
            knowledge_time = memory.canonical_bars[35]["as_of_time"]
        self.conn.execute(
            """INSERT INTO research__relationship_evidence
               (id, relationship_id, trial_id, validation_stage_id, experiment_run_id,
                dataset_snapshot_id, direction, sample_size, effect, uncertainty, payload,
                knowledge_time, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                stable_id("evidence", trial["id"]),
                rel_id,
                trial_id,
                stage_id,
                run_id,
                self.ids["snapshot"],
                ev["direction"],
                ev["sample_size"],
                ev["effect"],
                ev["uncertainty"],
                json.dumps({"source": "phase1-fixture"}),
                knowledge_time,
                now,
            ),
        )
        existing_evidence.add(trial_id)


def _assert_phase3_gate(self) -> None:
    row = self.conn.execute(
        "SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='phase3'"
    ).fetchone()
    if row is None or int(row["ingestion_enabled"]) != 0:
        raise RuntimeError("phase3 gate must keep ingestion_enabled=false")
