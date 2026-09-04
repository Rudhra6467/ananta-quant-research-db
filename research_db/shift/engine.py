"""Gate C shift detection. Observations/events, not predictions or certainty."""
from __future__ import annotations
import hashlib
import json
from typing import Any

KINDS = {"distribution_shift", "feature_drift", "regime_transition", "relationship_decay", "data_quality_shift", "market_structure_shift", "source_quality_degradation"}
REVIEW_STATUSES = {"detected", "false_positive", "inconclusive", "invalidated"}
SUBJECT_KINDS = {"instrument", "group", "market"}

class ShiftDenied(PermissionError):
    pass

class ShiftReview:
    def __init__(self) -> None:
        self.candidates: list[dict[str, Any]] = []
    def note(self, kind: str, event_code: str, basis: str):
        if kind not in KINDS:
            raise ShiftDenied(kind)
        row = {"kind": kind, "event": event_code, "basis": basis, "live_claim": False, "tape": "fixture"}
        self.candidates.append(row)
        return row

def _digest(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:16]

class ShiftRegistry:
    def __init__(self) -> None:
        self.specs: list[dict[str, Any]] = []
        self.runs: list[dict[str, Any]] = []
        self.candidates: list[dict[str, Any]] = []
        self.reviews: list[dict[str, Any]] = []
        self._seq = 0
    def define(self, code: str, version: str, kind: str, *, params: dict[str, Any], windows: dict[str, Any], subject_kind: str):
        if kind not in KINDS:
            raise ShiftDenied(kind)
        if subject_kind not in SUBJECT_KINDS:
            raise ShiftDenied(f"bad subject kind {subject_kind}")
        if any(s["code"] == code and s["version"] == version for s in self.specs):
            raise ShiftDenied(f"spec {code}@{version} exists")
        row = {"code": code, "version": version, "kind": kind, "params": dict(params), "windows": dict(windows), "subject_kind": subject_kind, "tape": "fixture"}
        self.specs.append(row)
        return row
    def versions(self, code: str):
        return [s["version"] for s in self.specs if s["code"] == code]
    def start_run(self, *, detector: str, version: str, snapshot: str, as_of: str, subject_kind: str, subject: str):
        spec = next((s for s in self.specs if s["code"] == detector and s["version"] == version), None)
        if spec is None:
            raise ShiftDenied("unknown detector spec")
        if spec["subject_kind"] != subject_kind:
            raise ShiftDenied("subject kind mismatch")
        self._seq += 1
        run_code = f"{detector}.{version}.{subject}.r{self._seq}"
        row = {"run_code": run_code, "detector": detector, "version": version, "snapshot": snapshot, "as_of": as_of, "subject_kind": subject_kind, "subject": subject, "kind": spec["kind"], "params": spec["params"], "windows": spec["windows"], "status": "running", "input_digest": None, "tape": "fixture", "live_claim": False}
        self.runs.append(row)
        return row
    def scan_annotated_events(self, run_code: str, events: list[dict[str, Any]]):
        run = self._run(run_code)
        found = []
        for ev in events:
            if ev.get("kind") not in {"shift", "regime_transition", "break"}:
                continue
            if ev.get("subject") != run["subject"]:
                continue
            if ev["knowledge_time"] > run["as_of"]:
                continue
            cand = {"candidate_code": f"{run_code}:{ev['code']}", "run_code": run_code, "event_code": ev["code"], "kind": run["kind"], "event_time": ev["event_time"], "knowledge_time": ev["knowledge_time"], "status": "detected", "certainty": False, "live_claim": False, "tape": "fixture", "note": "annotated event visible at as_of; not a production conclusion"}
            self.candidates.append(cand)
            found.append(cand)
        run["input_digest"] = _digest({"detector": run["detector"], "version": run["version"], "snapshot": run["snapshot"], "as_of": run["as_of"], "subject": run["subject"], "params": run["params"], "windows": run["windows"], "events": [c["event_code"] for c in found]})
        run["status"] = "complete"
        return found
    def review(self, candidate_code: str, status: str, note: str, knowledge_time: str):
        if status not in REVIEW_STATUSES:
            raise ShiftDenied(f"bad review {status}")
        cand = next((c for c in self.candidates if c["candidate_code"] == candidate_code), None)
        if cand is None:
            raise ShiftDenied("unknown candidate")
        if knowledge_time < cand["knowledge_time"]:
            raise ShiftDenied("PIT violation: review precedes candidate knowledge")
        row = {"candidate_code": candidate_code, "status": status, "note": note, "knowledge_time": knowledge_time, "live_claim": False}
        self.reviews.append(row)
        cand["status"] = status
        return row
    def rerun(self, run_code: str, events: list[dict[str, Any]]):
        prev = self._run(run_code)
        nxt = self.start_run(detector=prev["detector"], version=prev["version"], snapshot=prev["snapshot"], as_of=prev["as_of"], subject_kind=prev["subject_kind"], subject=prev["subject"])
        self.scan_annotated_events(nxt["run_code"], events)
        if nxt["input_digest"] != prev["input_digest"]:
            raise ShiftDenied("rerun digest mismatch")
        return nxt
    def _run(self, run_code: str):
        for run in self.runs:
            if run["run_code"] == run_code:
                return run
        raise ShiftDenied(f"unknown run {run_code}")

def fixture_shift_demo():
    from research_db.events.engine import fixture_events
    from research_db.lifecycle.engine import run_fixture_lifecycle
    from research_db.lifecycle.fixture import FIXTURE_CODE
    memory = run_fixture_lifecycle()
    evmem = fixture_events(memory.canonical_bars)
    peak = memory.canonical_bars[24]
    early = memory.canonical_bars[10]
    reg = ShiftRegistry()
    reg.define("DET_ANNOTATED_SHIFT", "v1", "regime_transition", params={"method": "annotated_replay", "threshold": None}, windows={"pre_bars": 4, "post_bars": 4}, subject_kind="instrument")
    run = reg.start_run(detector="DET_ANNOTATED_SHIFT", version="v1", snapshot=FIXTURE_CODE, as_of=peak["as_of_time"], subject_kind="instrument", subject=peak["instrument"])
    found = reg.scan_annotated_events(run["run_code"], evmem.events)
    early_run = reg.start_run(detector="DET_ANNOTATED_SHIFT", version="v1", snapshot=FIXTURE_CODE, as_of=early["as_of_time"], subject_kind="instrument", subject=peak["instrument"])
    early_found = reg.scan_annotated_events(early_run["run_code"], evmem.events)
    return reg, {"run": run, "found": found, "early_found": early_found, "events": evmem.events, "snapshot": FIXTURE_CODE, "as_of": peak["as_of_time"], "early_as_of": early["as_of_time"]}
