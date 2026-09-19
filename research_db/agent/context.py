"""Read-only agent context. PIT information set is mandatory."""
from __future__ import annotations
import hashlib
import json
from typing import Any
from research_db.agent.catalog import AVAILABLE, BLOCKED, CATALOG_VERSION, RESERVED, UNCERTAINTY
from research_db.agent.engine import AgentDenied

def _digest(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:16]

class AgentContext:
    def __init__(self, *, subject: str, snapshot: str, as_of: str, event_time: str | None = None) -> None:
        if not as_of or not snapshot or not subject:
            raise AgentDenied("information set requires subject, snapshot, and as_of")
        self.subject = subject
        self.snapshot = snapshot
        self.as_of = as_of
        self.event_time = event_time or as_of
        self.catalog_version = CATALOG_VERSION
        self.items: list[dict[str, Any]] = []
        self.uncertainty = "INSUFFICIENT_EVIDENCE"
        self.mutated = False
        self.live_claim = False
    def observe(self, capability: str, ref: str, knowledge_time: str, layer: str | None = None):
        if capability in BLOCKED:
            raise AgentDenied(f"capability blocked: {capability}")
        if capability in RESERVED:
            raise AgentDenied(f"capability reserved, not authorized: {capability}")
        if capability not in AVAILABLE:
            raise AgentDenied(f"capability not on catalog: {capability}")
        if not knowledge_time:
            raise AgentDenied("provenance knowledge_time required")
        if knowledge_time > self.as_of:
            raise AgentDenied("PIT violation: future knowledge cannot enter agent context")
        item = {"capability": capability, "layer": layer or AVAILABLE[capability], "ref": ref, "knowledge_time": knowledge_time}
        self.items.append(item)
        return item
    def set_uncertainty(self, token: str) -> None:
        if token not in UNCERTAINTY:
            raise AgentDenied(f"unknown uncertainty token {token}")
        self.uncertainty = token
    def decide(self, *_a, **_k) -> None:
        raise AgentDenied("Gate D cannot issue decisions")
    def digest(self) -> str:
        return _digest({"subject": self.subject, "snapshot": self.snapshot, "as_of": self.as_of, "catalog": self.catalog_version, "items": self.items, "uncertainty": self.uncertainty})
    def as_dict(self):
        return {"subject": self.subject, "event_time": self.event_time, "knowledge_time": self.as_of, "snapshot": self.snapshot, "catalog_version": self.catalog_version, "items": list(self.items), "uncertainty": self.uncertainty, "mutated": self.mutated, "live_claim": self.live_claim, "digest": self.digest()}

def fixture_agent_context():
    from research_db.events.engine import fixture_events
    from research_db.lifecycle.engine import run_fixture_lifecycle
    from research_db.lifecycle.fixture import FIXTURE_CODE, INSTRUMENT
    memory = run_fixture_lifecycle()
    evmem = fixture_events(memory.canonical_bars)
    early = memory.canonical_bars[10]
    late = memory.canonical_bars[24]
    ctx = AgentContext(subject=INSTRUMENT, snapshot=FIXTURE_CODE, as_of=early["as_of_time"], event_time=early["event_time"])
    ctx.observe("snapshot_identity", FIXTURE_CODE, early["as_of_time"])
    ctx.observe("current_market_state", early["event_time"], early["as_of_time"])
    ctx.set_uncertainty("INSUFFICIENT_EVIDENCE")
    later_event = next(e for e in evmem.events if e["code"] == "E_SHIFT_T24")
    return ctx, {"early_as_of": early["as_of_time"], "late_as_of": late["as_of_time"], "later_event": later_event, "snapshot": FIXTURE_CODE}
