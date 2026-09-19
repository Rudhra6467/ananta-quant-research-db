from __future__ import annotations
from typing import Iterable
from research_db.activation.charter import ActivationCharter
from research_db.ingest.contract import IngestBatch, IngestDenied, ProviderKind, RawRecord, SourceProvider
from research_db.ingest.validate import validate_ohlcv
INGESTION_ENABLED = False

class IngestionOrchestrator:
    def __init__(self) -> None:
        self.seen: set[tuple[str, str]] = set()
        self.batches: list[IngestBatch] = []
    def run(self, provider: SourceProvider, *, run_code: str, snapshot_code: str, charter: ActivationCharter | None = None) -> IngestBatch:
        kind = getattr(provider, "kind", "")
        if kind == ProviderKind.LIVE:
            if INGESTION_ENABLED is not True:
                if charter is None:
                    raise IngestDenied("live provider forbidden while INGESTION_ENABLED is false")
                if not charter.authorizes(source_code=getattr(provider, "code", ""), snapshot_code=snapshot_code, run_code=run_code):
                    raise IngestDenied("live provider not authorized by charter")
        elif kind not in {ProviderKind.FIXTURE, ProviderKind.REPLAY}:
            raise IngestDenied(f"unsupported provider kind {kind}")
        batch = IngestBatch(run_code=run_code, snapshot_code=snapshot_code, provider_kind=kind)
        records: Iterable[RawRecord] = provider.records()
        for rec in records:
            key = (rec.source_code, rec.source_record_id)
            if key in self.seen:
                batch.duplicates += 1
                continue
            verdict = validate_ohlcv(rec.payload, event_time=rec.event_time, knowledge_time=rec.knowledge_time)
            if not verdict.ok:
                batch.quarantined.append({"source_record_id": rec.source_record_id, "reason": verdict.reason, "event_time": rec.event_time})
                continue
            self.seen.add(key)
            batch.accepted.append(rec)
        self.batches.append(batch)
        return batch
