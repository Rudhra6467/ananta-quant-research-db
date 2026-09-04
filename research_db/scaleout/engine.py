"""Gate F scale-out readiness. Plans and fixtures only. Not activation."""
from __future__ import annotations
from typing import Any
from research_db.ingest.validate import validate_ohlcv
LAB10 = ("BTC-USD-SPOT","ETH-USD-SPOT","SOL-USD-SPOT","XRP-USD-SPOT","ADA-USD-SPOT","AVAX-USD-SPOT","LINK-USD-SPOT","DOGE-USD-SPOT","LTC-USD-SPOT","BCH-USD-SPOT")
ONTOLOGY = ("market","asset_class","sector","category","group","asset","instrument")
WORLDS = ("REALIZED_HISTORY","HISTORICAL_REPLAY","COUNTERFACTUAL","SYNTHETIC_SIMULATION")
PROMOTION = ("stable","decaying","regime_dependent","asset_dependent","failed","inconclusive")
LINEAGE = ("raw","canonical","feature","state","regime","relationship","hypothesis","prediction","decision","outcome","validation")
CROSS_ASSET = {"declared_relationship":"supported","analogue_pair":"supported","group_membership":"supported","correlation_matrix":"deferred_no_cube","pca_factor":"deferred_no_cube","network_graph":"deferred"}
class ScaleDenied(PermissionError):
    pass
class ScaleoutRegistry:
    def __init__(self) -> None:
        self.instruments = [{"code": c, "venue": "KRAKEN", "market": "crypto", "ingested": False} for c in LAB10]
        self.instruments[0]["fixture"] = True
        self.instruments[1]["fixture"] = True
        self.worlds = [{"code": w, "isolated": True} for w in WORLDS]
        self.quality = []
        self.promotions = [{"state": s, "automatic": False} for s in PROMOTION]
        self.lineage_status = {step: "contracted" for step in LINEAGE}
    def mark_lineage(self, step, status):
        if step not in self.lineage_status:
            raise ScaleDenied(step)
        self.lineage_status[step] = status
    def quality_check(self, payload, *, event_time, knowledge_time, seen):
        issues = []
        verdict = validate_ohlcv(payload, event_time=event_time, knowledge_time=knowledge_time)
        if not verdict.ok:
            issues.append(verdict.reason)
        if event_time in seen:
            issues.append("duplicate")
        if knowledge_time < event_time:
            issues.append("timestamp_error")
        row = {"event_time": event_time, "ok": not issues, "issues": issues, "quarantine": bool(issues)}
        self.quality.append(row)
        return row
    def onboard_allowed(self, instrument):
        return instrument in LAB10
    def ingested(self):
        return any(i.get("ingested") for i in self.instruments)

def fixture_scale_demo():
    from research_db.agent.context import AgentContext
    from research_db.events.engine import fixture_events
    from research_db.group.engine import GroupingEngine
    from research_db.lab.engine import Laboratory
    from research_db.lifecycle.engine import run_fixture_lifecycle
    from research_db.lifecycle.fixture import FIXTURE_CODE, INSTRUMENT
    from research_db.paper.session import PaperSession
    from research_db.shift.engine import ShiftRegistry
    memory = run_fixture_lifecycle()
    early, later = memory.canonical_bars[10], memory.canonical_bars[24]
    groups = GroupingEngine()
    groups.define_group("G_CRYPTO_MAJORS", "planned majors", "group")
    groups.assign(group="G_CRYPTO_MAJORS", member_kind="instrument", member=INSTRUMENT, effective_time=early["event_time"], knowledge_time=early["as_of_time"])
    groups.assign(group="G_CRYPTO_MAJORS", member_kind="instrument", member="ETH-USD-SPOT", effective_time=early["event_time"], knowledge_time=early["as_of_time"])
    evmem = fixture_events(memory.canonical_bars)
    shifts = ShiftRegistry()
    shifts.define("DET_ANNOTATED_SHIFT", "v1", "regime_transition", params={"method": "annotated_replay"}, windows={"pre_bars": 4, "post_bars": 4}, subject_kind="instrument")
    srun = shifts.start_run(detector="DET_ANNOTATED_SHIFT", version="v1", snapshot=FIXTURE_CODE, as_of=later["as_of_time"], subject_kind="instrument", subject=INSTRUMENT)
    shifts.scan_annotated_events(srun["run_code"], evmem.events)
    ctx = AgentContext(subject=INSTRUMENT, snapshot=FIXTURE_CODE, as_of=early["as_of_time"], event_time=early["event_time"])
    ctx.observe("snapshot_identity", FIXTURE_CODE, early["as_of_time"])
    ctx.observe("members_as_of", "G_CRYPTO_MAJORS", early["as_of_time"])
    ctx.set_uncertainty("INSUFFICIENT_EVIDENCE")
    lab = Laboratory()
    lab.define("EXP_SCALE_READY", "v1", "Architecture path across two subjects", snapshot=FIXTURE_CODE)
    lab.add_cohort("COHORT_MAJORS", "EXP_SCALE_READY", "v1")
    lrun = lab.start_run(experiment="EXP_SCALE_READY", version="v1", cohort="COHORT_MAJORS", snapshot=FIXTURE_CODE, as_of=early["as_of_time"])
    lab.attach(lrun["run_code"], "snapshot", FIXTURE_CODE, early["as_of_time"])
    lab.complete(lrun["run_code"], "inconclusive", "two identities, one tape; not performance")
    paper = PaperSession()
    paper.define("PD_SCALE_WAIT", "v1", "AVERAGE", "Wait until more subjects have tape")
    prec = paper.decide_from_context(definition="PD_SCALE_WAIT", version="v1", context=ctx, action="WAIT", reason="ETH identity only; no second tape")
    paper.realize_outcome(prec["run_code"], event_time=later["event_time"], knowledge_time=later["as_of_time"], note="later path")
    paper.evaluate(prec["run_code"], "inconclusive", "readiness demo not edge", later["as_of_time"])
    reg = ScaleoutRegistry()
    for step, status in {"raw":"fixture_only","canonical":"fixture_only","feature":"requested_only","state":"fixture_only","regime":"fixture_only","relationship":"declared","hypothesis":"fixture_only","prediction":"declared_no_engine","decision":"paper_zero_capital","outcome":"fixture_only","validation":"inconclusive"}.items():
        reg.mark_lineage(step, status)
    return reg, {"members": [m["member"] for m in groups.members_as_of("G_CRYPTO_MAJORS", early["event_time"], early["as_of_time"])], "paper": prec, "lab": lab.results[-1], "ingested": reg.ingested(), "worlds": [w["code"] for w in reg.worlds]}
