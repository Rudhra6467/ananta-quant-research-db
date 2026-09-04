from research_db.persist.store import FixtureStore, LiveQueryDenied, open_evidence_store, open_fixture_store
from research_db.persist import observe as phase4_observe
from research_db.persist import state as phase5_state
from research_db.persist import hypothesis as phase6_hypothesis
from research_db.persist import measure as phase7_measure
from research_db.persist import group as phase8_group
from research_db.persist import analyze as phase9_analyze
from research_db.persist import regime as phase10_regime
from research_db.persist import events as phase11_events
from research_db.persist import relate as phase12_relate
from research_db.persist import memorytier as phase14_memory
from research_db.persist import security as phase15_security
from research_db.persist import iface as phase16_iface
from research_db.persist import agent as phase17_agent
from research_db.persist import paper as phase18_paper
from research_db.persist import expansion as phase19_expansion
from research_db.persist import ingest as activation_a
from research_db.persist import lab as activation_b
from research_db.persist import shift as activation_c
from research_db.persist import agentd as activation_d
from research_db.persist import papere as activation_e
from research_db.persist import scaleout as activation_f
from research_db.persist import n2 as activation_n2

phase4_observe.bind(FixtureStore)
phase5_state.bind(FixtureStore)
phase6_hypothesis.bind(FixtureStore)
phase7_measure.bind(FixtureStore)
phase8_group.bind(FixtureStore)
phase9_analyze.bind(FixtureStore)
phase10_regime.bind(FixtureStore)
phase11_events.bind(FixtureStore)
phase12_relate.bind(FixtureStore)
phase14_memory.bind(FixtureStore)
phase15_security.bind(FixtureStore)
phase16_iface.bind(FixtureStore)
phase17_agent.bind(FixtureStore)
phase18_paper.bind(FixtureStore)
phase19_expansion.bind(FixtureStore)
activation_a.bind(FixtureStore)
activation_b.bind(FixtureStore)
activation_c.bind(FixtureStore)
activation_d.bind(FixtureStore)
activation_e.bind(FixtureStore)
activation_f.bind(FixtureStore)
activation_n2.bind(FixtureStore)


def open_observation_store(path: str = ":memory:"):
    store = open_fixture_store(path)
    store.install_phase4()
    return store


def open_state_store(path: str = ":memory:"):
    store = open_observation_store(path)
    store.install_phase5()
    return store


def open_hypothesis_store(path: str = ":memory:"):
    store = open_state_store(path)
    store.install_phase3()
    store.install_phase6()
    return store


def open_measurement_store(path: str = ":memory:"):
    store = open_hypothesis_store(path)
    store.install_phase7()
    return store


def open_group_store(path: str = ":memory:"):
    store = open_measurement_store(path)
    store.install_phase8()
    return store


def open_analytical_store(path: str = ":memory:"):
    store = open_group_store(path)
    store.install_phase9()
    return store


def open_regime_store(path: str = ":memory:"):
    store = open_analytical_store(path)
    store.install_phase10()
    return store


def open_event_store(path: str = ":memory:"):
    store = open_regime_store(path)
    store.install_phase11()
    return store


def open_relate_store(path: str = ":memory:"):
    store = open_event_store(path)
    store.install_phase12()
    store.install_phase13()
    return store


def open_governance_store(path: str = ":memory:"):
    store = open_relate_store(path)
    store.install_phase14()
    store.install_phase15()
    store.install_phase16()
    return store


def open_closed_loop_store(path: str = ":memory:"):
    store = open_governance_store(path)
    store.install_phase17()
    store.install_phase18()
    store.install_phase19()
    store.install_phase20()
    return store


def open_activation_store(path: str = ":memory:"):
    store = open_closed_loop_store(path)
    store.install_activation_a()
    return store


def open_laboratory_store(path: str = ":memory:"):
    store = open_activation_store(path)
    store.install_activation_b()
    return store


def open_shift_store(path: str = ":memory:"):
    store = open_laboratory_store(path)
    store.install_activation_c()
    return store


def open_agent_catalog_store(path: str = ":memory:"):
    store = open_shift_store(path)
    store.install_activation_d()
    return store


def open_paper_session_store(path: str = ":memory:"):
    store = open_agent_catalog_store(path)
    store.install_activation_e()
    return store


def open_scaleout_store(path: str = ":memory:"):
    store = open_paper_session_store(path)
    store.install_activation_f()
    return store


def open_n2_store(path: str = ":memory:"):
    store = open_scaleout_store(path)
    store.install_activation_n2()
    return store


__all__ = [
    "FixtureStore",
    "LiveQueryDenied",
    "open_evidence_store",
    "open_fixture_store",
    "open_observation_store",
    "open_state_store",
    "open_hypothesis_store",
    "open_measurement_store",
    "open_group_store",
    "open_analytical_store",
    "open_regime_store",
    "open_event_store",
    "open_relate_store",
    "open_governance_store",
    "open_closed_loop_store",
    "open_activation_store",
    "open_laboratory_store",
    "open_shift_store",
    "open_agent_catalog_store",
    "open_paper_session_store",
    "open_scaleout_store",
    "open_n2_store",
]
