"""Gate B laboratory. Fixture/replay only. Results are not market truth."""
from __future__ import annotations
import hashlib
import json
from typing import Any

RESULT_STATUSES = {"supported", "contradicted", "inconclusive", "invalidated", "insufficient"}
SOURCE_KINDS = {"snapshot", "observation", "evidence", "measurement", "hypothesis", "regime", "bar"}

class LaboratoryDenied(PermissionError):
    pass

class ExperimentSpec:
    def __init__(self, code: str, snapshot: str, question: str) -> None:
        if not code or not snapshot:
            raise LaboratoryDenied("experiment needs code and snapshot")
        self.code = code
        self.snapshot = snapshot
        self.question = question
        self.results: list[dict[str, Any]] = []
    def record(self, status: str, note: str, measurement_code: str | None = None):
        if status not in RESULT_STATUSES:
            raise LaboratoryDenied(f"bad status {status}")
        row = {"status": status, "note": note, "measurement": measurement_code, "tape": "fixture"}
        self.results.append(row)
        return row

def _digest(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]

class Laboratory:
    def __init__(self) -> None:
        self.definitions: list[dict[str, Any]] = []
        self.cohorts: list[dict[str, Any]] = []
        self.runs: list[dict[str, Any]] = []
        self.results: list[dict[str, Any]] = []
        self.links: list[dict[str, Any]] = []
        self._seq = 0
    def define(self, code: str, version: str, question: str, *, snapshot: str, hypothesis: str | None = None, measurement: str | None = None):
        if any(d["code"] == code and d["version"] == version for d in self.definitions):
            raise LaboratoryDenied(f"definition {code}@{version} exists")
        row = {"code": code, "version": version, "question": question, "snapshot": snapshot, "hypothesis": hypothesis, "measurement": measurement, "status": "active", "tape": "fixture"}
        self.definitions.append(row)
        return row
    def versions(self, code: str) -> list[str]:
        return [d["version"] for d in self.definitions if d["code"] == code]
    def add_cohort(self, code: str, experiment: str, version: str, note: str = ""):
        if not any(d["code"] == experiment and d["version"] == version for d in self.definitions):
            raise LaboratoryDenied("unknown experiment definition")
        row = {"code": code, "experiment": experiment, "version": version, "note": note}
        self.cohorts.append(row)
        return row
    def start_run(self, *, experiment: str, version: str, cohort: str, snapshot: str, as_of: str):
        dfn = next((d for d in self.definitions if d["code"] == experiment and d["version"] == version), None)
        if dfn is None:
            raise LaboratoryDenied("unknown experiment definition")
        if not any(c["code"] == cohort and c["experiment"] == experiment for c in self.cohorts):
            raise LaboratoryDenied("unknown cohort")
        if dfn["snapshot"] != snapshot:
            raise LaboratoryDenied("snapshot mismatch with definition")
        self._seq += 1
        run_code = f"{experiment}.{version}.{cohort}.r{self._seq}"
        row = {"run_code": run_code, "experiment": experiment, "version": version, "cohort": cohort, "snapshot": snapshot, "as_of": as_of, "status": "running", "input_digest": None, "tape": "fixture"}
        self.runs.append(row)
        return row
    def attach(self, run_code: str, source_kind: str, source_ref: str, knowledge_time: str):
        if source_kind not in SOURCE_KINDS:
            raise LaboratoryDenied(f"bad source kind {source_kind}")
        run = self._run(run_code)
        if knowledge_time > run["as_of"]:
            raise LaboratoryDenied("PIT violation: future knowledge cannot enter the information set")
        link = {"run_code": run_code, "source_kind": source_kind, "source_ref": source_ref, "knowledge_time": knowledge_time}
        self.links.append(link)
        return link
    def complete(self, run_code: str, status: str, note: str):
        if status not in RESULT_STATUSES:
            raise LaboratoryDenied(f"bad result {status}")
        run = self._run(run_code)
        run["input_digest"] = self._input_digest(run)
        run["status"] = "complete"
        result = {"run_code": run_code, "experiment": run["experiment"], "version": run["version"], "cohort": run["cohort"], "snapshot": run["snapshot"], "as_of": run["as_of"], "status": status, "note": note, "input_digest": run["input_digest"], "tape": "fixture"}
        self.results.append(result)
        return result
    def rerun(self, run_code: str):
        prev = self._run(run_code)
        prev_links = [l for l in self.links if l["run_code"] == run_code]
        prev_result = next(r for r in self.results if r["run_code"] == run_code)
        nxt = self.start_run(experiment=prev["experiment"], version=prev["version"], cohort=prev["cohort"], snapshot=prev["snapshot"], as_of=prev["as_of"])
        for link in prev_links:
            self.attach(nxt["run_code"], link["source_kind"], link["source_ref"], link["knowledge_time"])
        result = self.complete(nxt["run_code"], prev_result["status"], prev_result["note"])
        if result["input_digest"] != prev["input_digest"]:
            raise LaboratoryDenied("rerun digest mismatch")
        if nxt["run_code"] == prev["run_code"]:
            raise LaboratoryDenied("rerun must be a new run identity")
        return nxt
    def results_for(self, experiment: str):
        return [r for r in self.results if r["experiment"] == experiment]
    def _run(self, run_code: str):
        for run in self.runs:
            if run["run_code"] == run_code:
                return run
        raise LaboratoryDenied(f"unknown run {run_code}")
    def _input_digest(self, run):
        links = [{"k": l["source_kind"], "r": l["source_ref"], "t": l["knowledge_time"]} for l in self.links if l["run_code"] == run["run_code"]]
        links.sort(key=lambda x: (x["k"], x["r"], x["t"]))
        return _digest({"experiment": run["experiment"], "version": run["version"], "cohort": run["cohort"], "snapshot": run["snapshot"], "as_of": run["as_of"], "links": links})

def fixture_rsi_experiment():
    from research_db.lifecycle.engine import run_fixture_lifecycle
    from research_db.lifecycle.fixture import FIXTURE_CODE
    memory = run_fixture_lifecycle()
    boundary = memory.canonical_bars[24]
    as_of = boundary["as_of_time"]
    future = memory.canonical_bars[-1]["as_of_time"]
    lab = Laboratory()
    lab.define("EXP_RSI14_FWD_RET", "v1", "Does RSI(14)<35 associate with next-4h return on BTC 1h fixture?", snapshot=FIXTURE_CODE, hypothesis="H_RSI14_OVERSOLD_4H", measurement="effect_size.mean_forward_return.v1")
    lab.add_cohort("COHORT_BTC_1H_A", "EXP_RSI14_FWD_RET", "v1", "first fixture cohort")
    run = lab.start_run(experiment="EXP_RSI14_FWD_RET", version="v1", cohort="COHORT_BTC_1H_A", snapshot=FIXTURE_CODE, as_of=as_of)
    lab.attach(run["run_code"], "snapshot", FIXTURE_CODE, as_of)
    lab.attach(run["run_code"], "bar", boundary["event_time"], as_of)
    lab.attach(run["run_code"], "hypothesis", "H_RSI14_OVERSOLD_4H", as_of)
    lab.attach(run["run_code"], "measurement", "effect_size.mean_forward_return.v1", as_of)
    result = lab.complete(run["run_code"], "inconclusive", "n too small on 48-bar fixture; insufficient evidence")
    return lab, {"run": run, "result": result, "as_of": as_of, "future": future, "snapshot": FIXTURE_CODE}
