import pytest
from research_db.events.engine import fixture_events
from research_db.lifecycle.engine import run_fixture_lifecycle
from research_db.persist import LiveQueryDenied, open_relate_store
from research_db.relate.engine import AnalogueIndex, RelationDenied, RelationGraph

def test_declared_co_member_link_is_temporal() -> None:
    g = RelationGraph()
    g.link(left_kind="instrument", left="BTC-USD-SPOT", relation="co_member", right_kind="instrument", right="ETH-USD-SPOT", effective_time="2026-01-02T00:00:00+00:00", knowledge_time="2026-01-02T06:00:00+00:00", via="GRP_MAJORS")
    assert g.links_as_of("2026-01-01T00:00:00+00:00") == []
    assert len(g.links_as_of("2026-01-02T06:00:00+00:00")) == 1
    with pytest.raises(RelationDenied):
        g.link(left_kind="instrument", left="X", relation="causes", right_kind="instrument", right="Y", effective_time="t", knowledge_time="t")

def test_analogue_has_no_score() -> None:
    idx = AnalogueIndex()
    row = idx.pair("E_BREAK_T20", "E_SHIFT_T24", "same_episode_onset_vs_peak", "2026-01-03T00:00:00+00:00")
    assert row["score"] == ""
    with pytest.raises(RelationDenied):
        idx.pair("E", "E", "x", "t")

def test_persist_relations_and_analogues() -> None:
    memory = run_fixture_lifecycle()
    store = open_relate_store()
    store.persist_memory(memory)
    store.persist_events(fixture_events(memory.canonical_bars))
    g = RelationGraph()
    g.link(left_kind="instrument", left="BTC-USD-SPOT", relation="concurrent", right_kind="instrument", right="ETH-USD-SPOT", effective_time="2026-01-02T00:00:00+00:00", knowledge_time="2026-01-02T06:00:00+00:00", via="GRP_MAJORS")
    assert store.persist_relations(g)["links"] == 1
    idx = AnalogueIndex()
    idx.pair("E_BREAK_T20", "E_SHIFT_T24", "onset_vs_peak", memory.canonical_bars[-1]["as_of_time"])
    assert store.persist_analogues(idx)["analogues"] == 1
    score_cols = [r[1] for r in store.conn.execute("PRAGMA table_info(research__event_analogue_link)")]
    assert "score" not in score_cols
    with pytest.raises(LiveQueryDenied):
        store.live().execute("SELECT left_code FROM research__cross_subject_link")
