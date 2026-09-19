"""Gate E paper session. Zero capital. Same PIT boundary as Gate D."""
from __future__ import annotations
import hashlib, json
from typing import Any
from research_db.agent.context import AgentContext
from research_db.paper.engine import ACTIONS, PROFILES, PaperDenied, PaperLedger
POLICY_ACTIONS = ACTIONS | {"EXIT", "REDUCE", "INCREASE"}
EVAL_STATUSES = {"pending", "favorable", "unfavorable", "inconclusive", "invalidated"}
PRED_STATUSES = {"declared", "insufficient", "disagreed"}
RISK_STATUSES = {"ok", "constrained", "insufficient", "invalid"}

def _digest(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:16]

class PaperSession:
    def __init__(self, ledger: PaperLedger | None = None) -> None:
        self.ledger = ledger or PaperLedger()
        self.definitions, self.predictions, self.risks, self.records, self.outcomes, self.evaluations = [], [], [], [], [], []
        self._seq = 0
    def define(self, code, version, policy, question):
        if policy not in PROFILES:
            raise PaperDenied(f"unknown policy {policy}")
        if any(d["code"] == code and d["version"] == version for d in self.definitions):
            raise PaperDenied("definition exists")
        row = {"code": code, "version": version, "policy": policy, "question": question}
        self.definitions.append(row); return row
    def declare_prediction(self, *, run_code, target, horizon, uncertainty, model, status="insufficient"):
        if status not in PRED_STATUSES:
            raise PaperDenied(status)
        row = {"run_code": run_code, "target": target, "horizon": horizon, "uncertainty": uncertainty, "model": model, "status": status, "engine": None}
        self.predictions.append(row); return row
    def assess_risk(self, *, run_code, policy_version, status, note):
        if status not in RISK_STATUSES:
            raise PaperDenied(status)
        row = {"run_code": run_code, "policy_version": policy_version, "status": status, "note": note, "capital": 0, "executable": False}
        self.risks.append(row); return row
    def decide_from_context(self, *, definition, version, context: AgentContext, action, reason):
        dfn = next((d for d in self.definitions if d["code"] == definition and d["version"] == version), None)
        if dfn is None:
            raise PaperDenied("unknown decision definition")
        if action not in POLICY_ACTIONS:
            raise PaperDenied(f"unknown action {action}")
        for item in context.items:
            if item["knowledge_time"] > context.as_of:
                raise PaperDenied("PIT violation: context item after as_of")
        mapped = action if action in ACTIONS else "HOLD"
        if action == "WAIT":
            mapped = "WAIT"
        row = self.ledger.decide(dfn["policy"], mapped, context.as_of, reason, "agent_context", information_set=context.as_dict())
        if row["capital"] != 0 or row["live_order"] is not False:
            raise PaperDenied("zero-capital invariant broken")
        self._seq += 1
        rec = {"run_code": f"{definition}.{version}.r{self._seq}", "definition": definition, "version": version, "policy": dfn["policy"], "action": action, "mapped_action": mapped, "reason": reason, "subject": context.subject, "snapshot": context.snapshot, "as_of": context.as_of, "catalog_version": context.catalog_version, "context_digest": context.digest(), "capital": 0, "live_order": False, "tape": "fixture"}
        rec["input_digest"] = _digest({"definition": definition, "version": version, "policy": dfn["policy"], "action": action, "context": rec["context_digest"], "as_of": rec["as_of"], "snapshot": rec["snapshot"]})
        self.records.append(rec); return rec
    def realize_outcome(self, run_code, *, event_time, knowledge_time, note, value=None):
        rec = self._rec(run_code)
        if knowledge_time <= rec["as_of"]:
            raise PaperDenied("outcome knowledge_time must be after decision as_of")
        row = {"run_code": run_code, "event_time": event_time, "knowledge_time": knowledge_time, "note": note, "value": value, "status": "realized"}
        self.outcomes.append(row); return row
    def evaluate(self, run_code, status, note, knowledge_time):
        if status not in EVAL_STATUSES:
            raise PaperDenied(status)
        rec = self._rec(run_code)
        if knowledge_time <= rec["as_of"] and status != "pending":
            raise PaperDenied("evaluation of a realized outcome cannot use decision-time clock only")
        row = {"run_code": run_code, "status": status, "note": note, "knowledge_time": knowledge_time, "input_digest": rec["input_digest"]}
        self.evaluations.append(row); return row
    def rerun(self, run_code, context: AgentContext):
        prev = self._rec(run_code)
        nxt = self.decide_from_context(definition=prev["definition"], version=prev["version"], context=context, action=prev["action"], reason=prev["reason"])
        if nxt["input_digest"] != prev["input_digest"]:
            raise PaperDenied("rerun digest mismatch")
        return nxt
    def _rec(self, run_code):
        for r in self.records:
            if r["run_code"] == run_code:
                return r
        raise PaperDenied(f"unknown run {run_code}")

def fixture_paper_path():
    from research_db.agent.context import AgentContext
    from research_db.lifecycle.engine import run_fixture_lifecycle
    from research_db.lifecycle.fixture import FIXTURE_CODE, INSTRUMENT
    memory = run_fixture_lifecycle()
    early, later = memory.canonical_bars[10], memory.canonical_bars[24]
    ctx = AgentContext(subject=INSTRUMENT, snapshot=FIXTURE_CODE, as_of=early["as_of_time"], event_time=early["event_time"])
    ctx.observe("snapshot_identity", FIXTURE_CODE, early["as_of_time"])
    ctx.observe("current_market_state", early["event_time"], early["as_of_time"])
    ctx.set_uncertainty("INSUFFICIENT_EVIDENCE")
    session = PaperSession()
    session.define("PD_NO_ACTION_UNLESS_EVIDENCE", "v1", "AVERAGE", "Wait unless evidence is sufficient")
    rec = session.decide_from_context(definition="PD_NO_ACTION_UNLESS_EVIDENCE", version="v1", context=ctx, action="WAIT", reason="insufficient evidence at as_of")
    session.declare_prediction(run_code=rec["run_code"], target="forward_4h_return", horizon="4h", uncertainty="INSUFFICIENT_EVIDENCE", model="none", status="insufficient")
    session.assess_risk(run_code=rec["run_code"], policy_version="risk-paper-v1", status="insufficient", note="no budget; capital stays 0")
    session.realize_outcome(rec["run_code"], event_time=later["event_time"], knowledge_time=later["as_of_time"], note="path after decision; not knowable at as_of", value=(later["close"]-early["close"])/early["close"])
    ev = session.evaluate(rec["run_code"], "inconclusive", "n=1 fixture path; WAIT cannot be scored as edge", later["as_of_time"])
    return session, {"record": rec, "context": ctx, "early": early, "later": later, "evaluation": ev, "snapshot": FIXTURE_CODE}
