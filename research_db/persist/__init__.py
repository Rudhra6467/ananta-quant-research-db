from research_db.persist.store import FixtureStore, LiveQueryDenied, open_evidence_store, open_fixture_store
from research_db.persist import observe as phase4_observe
from research_db.persist import state as phase5_state

phase4_observe.bind(FixtureStore)
phase5_state.bind(FixtureStore)


def open_observation_store(path: str = ":memory:"):
    store = open_fixture_store(path)
    store.install_phase4()
    return store


def open_state_store(path: str = ":memory:"):
    store = open_observation_store(path)
    store.install_phase5()
    return store


__all__ = [
    "FixtureStore",
    "LiveQueryDenied",
    "open_evidence_store",
    "open_fixture_store",
    "open_observation_store",
    "open_state_store",
]
