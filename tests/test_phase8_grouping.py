from pathlib import Path

import pytest

from research_db.group.engine import GroupDenied, GroupingEngine, fixture_grouping
from research_db.lifecycle.engine import run_fixture_lifecycle
from research_db.persist import LiveQueryDenied, open_group_store

ROOT = Path(__file__).resolve().parents[1]
T0 = "2026-01-01T00:00:00+00:00"
T0_KNOW = "2026-01-01T12:00:00+00:00"
T1 = "2026-01-01T18:00:00+00:00"
T2 = "2026-01-02T12:00:00+00:00"


def test_identity_separate_from_membership() -> None:
    g = fixture_grouping()
    assert {row["code"] for row in g.groups} >= {"MKT_CRYPTO", "GRP_MAJORS"}
    assert all("effective_time" in m for m in g.memberships)


def test_self_membership_and_bad_kind_rejected() -> None:
    g = GroupingEngine()
    g.define_group("G", "G", "group")
    with pytest.raises(GroupDenied):
        g.assign(group="G", member_kind="group", member="G", effective_time=T0, knowledge_time=T0)
    with pytest.raises(GroupDenied):
        g.define_group("X", "X", "portfolio")
    with pytest.raises(GroupDenied):
        g.assign(group="G", member_kind="prediction", member="BTC", effective_time=T0, knowledge_time=T0)


def test_members_as_of_changes_and_keeps_history() -> None:
    g = fixture_grouping()
    a = [m["member"] for m in g.members_as_of("GRP_MAJORS", T1, T1, member_kind="instrument")]
    b = [m["member"] for m in g.members_as_of("GRP_MAJORS", T2, T2, member_kind="instrument")]
    assert a == ["BTC-USD-SPOT"]
    assert b == ["ETH-USD-SPOT"]
    assert a != b
    assert any(m["member"] == "BTC-USD-SPOT" and m["expiry_time"] == "2026-01-02T00:00:00+00:00" for m in g.memberships)


def test_knowledge_time_hides_unlearned_membership() -> None:
    g = fixture_grouping()
    early = g.members_as_of("GRP_MAJORS", T0, T0, member_kind="instrument")
    later = g.members_as_of("GRP_MAJORS", T0, T0_KNOW, member_kind="instrument")
    assert early == []
    assert [m["member"] for m in later] == ["BTC-USD-SPOT"]


def test_hierarchy_is_group_as_member() -> None:
    g = fixture_grouping()
    kids = [m["member"] for m in g.members_as_of("MKT_CRYPTO", T1, T1, member_kind="group")]
    assert kids == ["AC_CRYPTO_SPOT"]


def test_persisted_members_as_of_and_append_only() -> None:
    store = open_group_store()
    store.persist_memory(run_fixture_lifecycle())
    engine = fixture_grouping()
    stats = store.persist_groups(engine)
    assert stats["groups"] == 4
    assert stats["memberships"] >= 6
    assert store.members_as_of("GRP_MAJORS", T1, T1, "instrument") == ["BTC-USD-SPOT"]
    assert store.members_as_of("GRP_MAJORS", T2, T2, "instrument") == ["ETH-USD-SPOT"]
    assert store.members_as_of("GRP_MAJORS", T0, T0, "instrument") == []
    gate = store.conn.execute("SELECT ingestion_enabled FROM ops__schema_gate WHERE phase='phase8'").fetchone()
    assert int(gate["ingestion_enabled"]) == 0
    with pytest.raises(Exception):
        store.conn.execute("DELETE FROM research__group_membership")


def test_live_path_cannot_read_groups() -> None:
    store = open_group_store()
    store.persist_memory(run_fixture_lifecycle())
    store.persist_groups(fixture_grouping())
    live = store.live()
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT code FROM research__market_group")
    with pytest.raises(LiveQueryDenied):
        live.execute("SELECT member_code FROM research__group_membership")


def test_phase8_sql_has_no_aggregation_or_exchange() -> None:
    text = (ROOT / "sql" / "008_phase8_grouping.sql").read_text(encoding="utf-8").lower()
    assert "ingestion_enabled" in text and "false" in text
    assert "binance" not in text
    assert "aggregate" not in text
    assert "current_group" not in text
    assert "ranking" not in text
