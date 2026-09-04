from __future__ import annotations
from research_db.ingest.contract import ProviderKind, RawRecord
from research_db.lifecycle.engine import run_fixture_lifecycle
class FixtureSource:
    code = "fixture.ohlc"
    kind = ProviderKind.FIXTURE
    def records(self) -> list[RawRecord]:
        memory = run_fixture_lifecycle()
        out = []
        for raw in memory.raw_events:
            out.append(RawRecord(source_code=self.code, source_record_id=raw["source_record_id"], instrument=raw["instrument"], timeframe=raw["timeframe"], event_time=raw["event_time"], knowledge_time=raw.get("knowledge_time") or raw["event_time"], payload=raw["payload"], checksum=raw["checksum"], provider_kind=self.kind))
        return out
