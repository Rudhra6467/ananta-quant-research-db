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

phase4_observe.bind(FixtureStore)
phase5_state.bind(FixtureStore)
phase6_hypothesis.bind(FixtureStore)
phase7_measure.bind(FixtureStore)
phase8_group.bind(FixtureStore)
phase9_analyze.bind(FixtureStore)
phase10_regime.bind(FixtureStore)
phase11_events.bind(FixtureStore)
phase12_relate.bind(FixtureStore)


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
]
