from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Iterable, Protocol
class IngestDenied(PermissionError):
    pass
class ProviderKind:
    FIXTURE = "fixture"
    REPLAY = "replay"
    LIVE = "live"
@dataclass(frozen=True)
class RawRecord:
    source_code: str
    source_record_id: str
    instrument: str
    timeframe: str
    event_time: str
    knowledge_time: str
    payload: dict[str, Any]
    checksum: str
    provider_kind: str
class SourceProvider(Protocol):
    code: str
    kind: str
    def records(self) -> Iterable[RawRecord]: ...
@dataclass
class IngestBatch:
    run_code: str
    snapshot_code: str
    provider_kind: str
    accepted: list[RawRecord] = field(default_factory=list)
    quarantined: list[dict[str, Any]] = field(default_factory=list)
    duplicates: int = 0
