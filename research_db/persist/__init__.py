from research_db.persist.store import FixtureStore, LiveQueryDenied, open_evidence_store, open_fixture_store
from research_db.persist import observe as phase4_observe

phase4_observe.bind(FixtureStore)


def open_observation_store(path: str = ":memory:"):
    store = open_fixture_store(path)
    store.install_phase4()
    return store


__all__ = [
    "FixtureStore",
    "LiveQueryDenied",
    "open_evidence_store",
    "open_fixture_store",
    "open_observation_store",
]
