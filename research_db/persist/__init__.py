from research_db.persist.store import FixtureStore, LiveQueryDenied, open_evidence_store, open_fixture_store
from research_db.persist import observe as phase4_observe
from research_db.persist import state as phase5_state
from research_db.persist import hypothesis as phase6_hypothesis
from research_db.persist import measure as phase7_measure

phase4_observe.bind(FixtureStore)
phase5_state.bind(FixtureStore)
phase6_hypothesis.bind(FixtureStore)
phase7_measure.bind(FixtureStore)


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


__all__ = [
    "FixtureStore",
    "LiveQueryDenied",
    "open_evidence_store",
    "open_fixture_store",
    "open_observation_store",
    "open_state_store",
    "open_hypothesis_store",
    "open_measurement_store",
]
