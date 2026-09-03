from pathlib import Path

import pytest

from research_db.lifecycle.engine import incremental_bar, run_fixture_lifecycle
from research_db.persist.store import LiveQueryDenied, open_evidence_store, open_fixture_store

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def loaded():
    memory = run_fixture_lifecycle()
    store = open_evidence_store()
    store.persist_memory(memory)
    stats = store.persist_evidence(memory)
    return memory, store, stats


def test_phase3_sql_does_not_enable_ingest() -> None:
    text = (ROOT / "sql" / "003_phase3_evidence.sql").read_text(encoding="utf-8")
    assert "ingestion_enabled" in text
    assert "false" in text
    assert "binance" not in text.lower()
    assert "kraken" not in text.lower()


def test_phase2_schema_still_omits_evidence() -> None:
    store = open_fixture_store()
    tables = {r[0] for r in store.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "research__relationship_evidence" not in tables


def test_evidence_matches_phase1_memory(loaded) -> None:
    memory, store, stats = loaded
    assert stats["evidence"] == len(memory.evidence)
    assert stats["trials"] == len(memory.experiment_trials)
    assert stats["experiment_runs"] == 1
    rows = store.conn.execute(
        """SELECT r.code AS relationship, s.code AS stage, e.direction, e.sample_size, e.effect
           FROM research__relationship_evidence e
           JOIN research__relationship_definition r ON r.id = e.relationship_id
           JOIN research__validation_stage s ON s.id = e.validation_stage_id
           ORDER BY r.code, s.sort_order"""
    ).fetchall()
    expected = {(e["relationship"], e["stage"], e["direction"], e["sample_size"], e["effect"]) for e in memory.evidence}
    got = {(r["relationship"], r["stage"], r["direction"], r["sample_size"], r["effect"]) for r in rows}
    assert got == expected


def test_negative_and_insufficient_states_are_legal(loaded) -> None:
    _, store, _ = loaded
    check = store.conn.execute(
        "SELECT sql FROM sqlite_master WHERE name='research__relationship_evidence'"
    ).fetchone()["sql"]
    for state in ("untested", "supports", "contradicts", "inconclusive", "invalidated", "decayed"):
        assert state in check
    directions = {r["direction"] for r in store.conn.execute("SELECT direction FROM research__relationship_evidence")}
    assert directions <= {"untested", "supports", "contradicts", "inconclusive", "invalidated", "decayed"}


def test_evidence_is_append_only(loaded) -> None:
    _, store, _ = loaded
    row = store.conn.execute("SELECT id FROM research__relationship_evidence LIMIT 1").fetchone()
    with pytest.raises(Exception):
        store.conn.execute(
            "UPDATE research__relationship_evidence SET direction='supports' WHERE id=?",
            (row["id"],),
        )
    with pytest.raises(Exception):
        store.conn.execute("DELETE FROM research__relationship_evidence WHERE id=?", (row["id"],))


def test_reset_creates_cohort_and_keeps_history(loaded) -> None:
    memory, store, stats = loaded
    before = stats["evidence"]
    store.persist_reset_cohort(memory, "exp-fixture-rsi-region-reset")
    codes = {r["code"] for r in store.conn.execute("SELECT code FROM research__experiment_run")}
    assert "exp-fixture-rsi-region" in codes
    assert "exp-fixture-rsi-region-reset" in codes
    assert store.conn.execute("SELECT COUNT(*) AS n FROM research__relationship_evidence").fetchone()["n"] == before


def test_incremental_evidence_does_not_rescan_delete(loaded) -> None:
    memory, store, stats = loaded
    before = stats["evidence"]
    incremental_bar(memory)
    store.persist_incremental(memory)
    store.append_forward_evidence(memory, "R_RSI14_OVERSOLD_4H")
    after = store.conn.execute("SELECT COUNT(*) AS n FROM research__relationship_evidence").fetchone()["n"]
    assert after == before + 1
    stages = {r["code"] for r in store.conn.execute(
        """SELECT s.code FROM research__relationship_evidence e
           JOIN research__validation_stage s ON s.id = e.validation_stage_id"""
    )}
    assert stages >= {"HISTORICAL", "OOS", "FORWARD"}


def test_point_in_time_hides_later_evidence(loaded) -> None:
    memory, store, _ = loaded
    hist_as_of = memory.canonical_bars[35]["as_of_time"]
    visible = store.evidence_as_of(hist_as_of)
    assert visible
    assert {r["stage"] for r in visible} == {"HISTORICAL"}
    later = store.evidence_as_of(memory.canonical_bars[-1]["as_of_time"])
    assert {r["stage"] for r in later} == {"HISTORICAL", "OOS"}


def test_live_path_cannot_read_evidence(loaded) -> None:
    _, store, _ = loaded
    live = store.live()
    live.execute("SELECT event_time FROM ops__current_market_state")
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT direction FROM research__relationship_evidence")
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT code FROM research__experiment_run")


def test_current_summary_is_rebuildable_projection(loaded) -> None:
    memory, store, _ = loaded
    rows = list(store.conn.execute("SELECT * FROM analytics__relationship_current_summary"))
    assert len(rows) == len(memory.relationship_current_summary)
    store.conn.execute("DELETE FROM analytics__relationship_current_summary")
    store._persist_current_summaries(memory)
    assert store.conn.execute("SELECT COUNT(*) AS n FROM analytics__relationship_current_summary").fetchone()["n"] == len(rows)


def test_no_ranking_engine_and_no_exchange(loaded) -> None:
    _, store, _ = loaded
    tables = {r[0] for r in store.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "research__ranking_snapshot" not in tables
    notes = store.conn.execute("SELECT notes, ingestion_enabled FROM ops__schema_gate WHERE phase='phase3'").fetchone()
    assert int(notes["ingestion_enabled"]) == 0
