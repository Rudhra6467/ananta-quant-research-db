"""Fixture lifecycle: discover → evidence → rank → apply → increment.

Does not pre-materialize every RSI period on every bar.
Does not rescan research history on the live tick.
"""

from __future__ import annotations

from datetime import datetime
from statistics import mean
from typing import Any

from research_db.lifecycle import fixture
from research_db.lifecycle.features import rsi
from research_db.lifecycle.store import EmpiricalMemory

RSI_REGION = list(range(12, 18))
OVERSOLD = 35.0
LIVE_TABLES = {
    "current_market_state",
    "current_feature_value",
    "current_regime_state",
    "operational_applicability",
}


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def ingest_raw(memory: EmpiricalMemory, payloads: list[dict[str, Any]], run_id: str) -> None:
    snap = {
        "id": fixture.FIXTURE_CODE,
        "as_of_time": payloads[-1]["event_time"],
        "source": fixture.SOURCE,
    }
    if not any(s["id"] == snap["id"] for s in memory.dataset_snapshots):
        memory.append_fact(memory.dataset_snapshots, snap)
    memory.append_fact(
        memory.ingestion_runs,
        {"id": run_id, "snapshot": fixture.FIXTURE_CODE, "status": "complete", "n": len(payloads)},
    )
    known = {row["source_record_id"] for row in memory.raw_events}
    for payload in payloads:
        if payload["source_record_id"] in known:
            continue
        memory.append_fact(memory.raw_events, dict(payload))


def canonicalize(memory: EmpiricalMemory, run_id: str) -> None:
    memory.append_fact(
        memory.canonicalization_runs,
        {
            "id": run_id,
            "version": fixture.CANONICALIZATION_VERSION,
            "ingestion_run": memory.ingestion_runs[-1]["id"],
            "status": "complete",
        },
    )
    known = {row["event_time"] for row in memory.canonical_bars}
    for raw in memory.raw_events:
        if raw["event_time"] in known:
            continue
        event_time = _parse(raw["event_time"])
        as_of = fixture.received_at_for(event_time)
        p = raw["payload"]
        memory.append_fact(
            memory.canonical_bars,
            {
                "instrument": raw["instrument"],
                "venue": raw["venue"],
                "timeframe": raw["timeframe"],
                "event_time": raw["event_time"],
                "as_of_time": as_of.isoformat(),
                "open": p["open"],
                "high": p["high"],
                "low": p["low"],
                "close": p["close"],
                "volume": p["volume"],
                "source_record_id": raw["source_record_id"],
                "canonicalization_version": fixture.CANONICALIZATION_VERSION,
                "dataset_snapshot": fixture.FIXTURE_CODE,
            },
        )


def define_research_objects(memory: EmpiricalMemory) -> None:
    memory.feature_definitions["RSI"] = {
        "family": "RSI",
        "version": "v1",
        "topology": "ordered_discrete",
        "domain": {"period": {"min": 2, "max": 50}},
    }
    for period in RSI_REGION:
        key = f"RSI({period})"
        memory.parameter_sets[key] = {"feature": "RSI", "period": period, "signature": key}
    memory.parameter_regions["RSI(12-17)"] = {
        "feature": "RSI",
        "dimension": "period",
        "lo": 12,
        "hi": 17,
        "members": [f"RSI({p})" for p in RSI_REGION],
        "detection": "declared_for_fixture",
    }
    memory.relationship_definitions["R_RSI_REGION_OVERSOLD_4H"] = {
        "code": "R_RSI_REGION_OVERSOLD_4H",
        "antecedent": "RSI(12-17) < 35",
        "context": {"instrument": fixture.INSTRUMENT, "timeframe": fixture.TIMEFRAME},
        "outcome": {"name": "future_return", "horizon_bars": fixture.HORIZON_BARS},
        "version": "v1",
    }
    memory.relationship_definitions["R_RSI14_OVERSOLD_4H"] = {
        "code": "R_RSI14_OVERSOLD_4H",
        "antecedent": "RSI(14) < 35",
        "context": {"instrument": fixture.INSTRUMENT, "timeframe": fixture.TIMEFRAME},
        "outcome": {"name": "future_return", "horizon_bars": fixture.HORIZON_BARS},
        "version": "v1",
    }


def requested_parameter_sets() -> list[str]:
    return [f"RSI({p})" for p in RSI_REGION]


def persist_requested_observations(memory: EmpiricalMemory, bars: list[dict[str, Any]]) -> int:
    closes = [bar["close"] for bar in bars]
    created = 0
    existing = memory.observation_keys()
    for key in requested_parameter_sets():
        period = memory.parameter_sets[key]["period"]
        series = rsi(closes, period)
        memory.compute_log.append({"kind": "rsi", "parameter_set": key, "n_bars": len(closes)})
        for bar, value in zip(bars, series):
            if value is None:
                continue
            obs_key = (key, bar["event_time"])
            if obs_key in existing:
                continue
            memory.append_fact(
                memory.feature_observations,
                {
                    "feature": "RSI",
                    "feature_version": "v1",
                    "parameter_set": key,
                    "instrument": bar["instrument"],
                    "timeframe": bar["timeframe"],
                    "event_time": bar["event_time"],
                    "as_of_time": bar["as_of_time"],
                    "value": value,
                    "dataset_snapshot": bar["dataset_snapshot"],
                },
            )
            created += 1
            existing.add(obs_key)
    return created


def _returns(bars: list[dict[str, Any]], horizon: int) -> dict[str, float]:
    out: dict[str, float] = {}
    for i, bar in enumerate(bars):
        j = i + horizon
        if j >= len(bars):
            continue
        out[bar["event_time"]] = (bars[j]["close"] - bar["close"]) / bar["close"]
    return out


def _rsi_at(memory: EmpiricalMemory, parameter_set: str, event_time: str) -> float | None:
    for row in reversed(memory.feature_observations):
        if row["parameter_set"] == parameter_set and row["event_time"] == event_time:
            return float(row["value"])
    return None


def _region_median_rsi(memory: EmpiricalMemory, event_time: str) -> float | None:
    values = []
    for key in requested_parameter_sets():
        value = _rsi_at(memory, key, event_time)
        if value is not None:
            values.append(value)
    if not values:
        return None
    values.sort()
    mid = len(values) // 2
    if len(values) % 2:
        return values[mid]
    return (values[mid - 1] + values[mid]) / 2


def evaluate_relationship(
    memory: EmpiricalMemory,
    code: str,
    bars: list[dict[str, Any]],
    stage: str,
    start: int,
    end: int,
) -> dict[str, Any]:
    rel = memory.relationship_definitions[code]
    horizon = rel["outcome"]["horizon_bars"]
    window = bars[start:end]
    fwd = _returns(window, horizon)
    hits: list[float] = []
    for bar in window:
        event_time = bar["event_time"]
        if event_time not in fwd:
            continue
        if code == "R_RSI14_OVERSOLD_4H":
            value = _rsi_at(memory, "RSI(14)", event_time)
            triggered = value is not None and value < OVERSOLD
        else:
            value = _region_median_rsi(memory, event_time)
            triggered = value is not None and value < OVERSOLD
        if triggered:
            hits.append(fwd[event_time])
    sample = len(hits)
    effect = mean(hits) if hits else 0.0
    direction = "supports" if sample >= 3 and effect > 0 else "inconclusive" if sample < 3 else "contradicts"
    trial = {
        "id": f"{code}:{stage}",
        "relationship": code,
        "stage": stage,
        "status": "complete",
        "window": (start, end),
    }
    memory.append_fact(memory.experiment_trials, trial)
    ev = {
        "relationship": code,
        "trial": trial["id"],
        "stage": stage,
        "direction": direction,
        "sample_size": sample,
        "effect": round(effect, 8),
        "uncertainty": None if sample < 2 else round(max(abs(effect) * 0.25, 1e-6), 8),
    }
    memory.append_fact(memory.evidence, ev)
    return ev


def snapshot_ranks(memory: EmpiricalMemory, stage: str, as_of: str) -> None:
    rows = [e for e in memory.evidence if e["stage"] == stage]
    ranked = sorted(rows, key=lambda e: e["effect"], reverse=True)
    for i, ev in enumerate(ranked, start=1):
        memory.append_fact(
            memory.ranking_snapshots,
            {
                "relationship": ev["relationship"],
                "stage": stage,
                "scoring_model_version": "fixture-score-v1",
                "score": ev["effect"],
                "rank": i,
                "population_size": len(ranked),
                "cohort_label": "top10" if i == 1 else "next_band",
                "as_of_time": as_of,
            },
        )


def rebuild_projections(memory: EmpiricalMemory, bars: list[dict[str, Any]]) -> None:
    last = bars[-1]
    key = f"{last['instrument']}|{last['venue']}|{last['timeframe']}"
    memory.current_market_state[key] = {
        "instrument": last["instrument"],
        "venue": last["venue"],
        "timeframe": last["timeframe"],
        "event_time": last["event_time"],
        "as_of_time": last["as_of_time"],
        "close": last["close"],
        "state_version": f"state:{last['event_time']}",
    }
    for pset in requested_parameter_sets():
        value = _rsi_at(memory, pset, last["event_time"])
        memory.current_feature_value[pset] = {
            "parameter_set": pset,
            "event_time": last["event_time"],
            "as_of_time": last["as_of_time"],
            "value": value,
        }
    median = _region_median_rsi(memory, last["event_time"])
    regime = "oversold" if median is not None and median < OVERSOLD else "neutral"
    memory.current_regime_state[key] = {
        "regime_family": "rsi_region",
        "label": regime,
        "value": median,
        "event_time": last["event_time"],
        "as_of_time": last["as_of_time"],
        "provenance": "system_fixture",
    }
    hist = {e["relationship"]: e for e in memory.evidence if e["stage"] == "HISTORICAL"}
    oos = {e["relationship"]: e for e in memory.evidence if e["stage"] == "OOS"}
    for code, rel in memory.relationship_definitions.items():
        h = hist.get(code)
        o = oos.get(code)
        blended = None
        if h and o:
            blended = 0.4 * h["effect"] + 0.6 * o["effect"]
        elif h:
            blended = h["effect"]
        memory.relationship_current_summary[code] = {
            "relationship": code,
            "status": "research_only",
            "blended_score": blended,
            "historical_effect": None if not h else h["effect"],
            "oos_effect": None if not o else o["effect"],
            "scoring_model_version": "fixture-blend-v1",
            "source_watermark": last["event_time"],
        }
        applicable = regime == "oversold" and blended is not None and blended > 0
        memory.operational_applicability[code] = {
            "relationship": code,
            "active": applicable,
            "regime_bucket": regime,
            "score": blended,
            "state_version": f"state:{last['event_time']}",
            "antecedent": rel["antecedent"],
        }


def live_decide(memory: EmpiricalMemory) -> dict[str, Any]:
    state = memory.live_get("current_market_state")
    features = memory.live_get("current_feature_value")
    regime = memory.live_get("current_regime_state")
    apps = memory.live_get("operational_applicability")
    assert set(memory.live_query_log[-4:]) <= LIVE_TABLES
    active = [row for row in apps.values() if row["active"]]
    state_row = next(iter(state.values()))
    regime_row = next(iter(regime.values()))
    if not active:
        action = "SKIP"
        reason = "no applicable relationship"
        chosen = None
    elif regime_row["label"] != "oversold":
        action = "WAIT"
        reason = "regime not oversold"
        chosen = active[0]["relationship"]
    else:
        action = "ENTER"
        reason = "applicable oversold region"
        chosen = max(active, key=lambda r: r["score"] or 0)["relationship"]
    decision = {
        "action": action,
        "relationship": chosen,
        "event_time": state_row["event_time"],
        "as_of_time": state_row["as_of_time"],
        "state_version": state_row["state_version"],
        "reason": reason,
        "rsi14": None if "RSI(14)" not in features else features["RSI(14)"]["value"],
    }
    memory.append_fact(memory.decisions, decision)
    return decision


def attach_counterfactuals(memory: EmpiricalMemory, bars: list[dict[str, Any]]) -> None:
    by_time = {b["event_time"]: i for i, b in enumerate(bars)}
    for decision in memory.decisions:
        i = by_time.get(decision["event_time"])
        if i is None:
            continue
        j = i + fixture.HORIZON_BARS
        if j >= len(bars):
            realized = None
        else:
            realized = (bars[j]["close"] - bars[i]["close"]) / bars[i]["close"]
        for path in ("ENTER", "WAIT", "SKIP"):
            memory.append_fact(
                memory.counterfactuals,
                {
                    "decision_event_time": decision["event_time"],
                    "chosen_action": decision["action"],
                    "action_path": path,
                    "horizon_bars": fixture.HORIZON_BARS,
                    "realized_return": realized,
                },
            )


def incremental_bar(memory: EmpiricalMemory) -> dict[str, Any]:
    before_obs = len(memory.feature_observations)
    before_canon = len(memory.canonical_bars)
    payloads = fixture.build_raw_payloads(include_extra=True)
    ingest_raw(memory, payloads, run_id="ingest-increment")
    canonicalize(memory, run_id="canon-increment")
    new_bars = memory.canonical_bars[before_canon:]
    assert len(new_bars) == 1
    persist_requested_observations(memory, memory.canonical_bars)
    created = len(memory.feature_observations) - before_obs
    rebuild_projections(memory, memory.canonical_bars)
    return {
        "new_canonical_bars": len(new_bars),
        "new_feature_observations": created,
        "expected_new_observations": len(requested_parameter_sets()),
        "current_event_time": memory.canonical_bars[-1]["event_time"],
    }


def run_fixture_lifecycle() -> EmpiricalMemory:
    memory = EmpiricalMemory()
    payloads = fixture.build_raw_payloads()
    ingest_raw(memory, payloads, run_id="ingest-base")
    canonicalize(memory, run_id="canon-base")
    define_research_objects(memory)
    persist_requested_observations(memory, memory.canonical_bars)
    bars = memory.canonical_bars
    split = 36
    memory.append_fact(
        memory.experiment_runs,
        {
            "id": "exp-fixture-rsi-region",
            "snapshot": fixture.FIXTURE_CODE,
            "code_commit": "phase1-fixture",
            "status": "complete",
        },
    )
    for code in memory.relationship_definitions:
        evaluate_relationship(memory, code, bars, "HISTORICAL", 0, split)
        evaluate_relationship(memory, code, bars, "OOS", split, len(bars))
    as_of = bars[split - 1]["as_of_time"]
    snapshot_ranks(memory, "HISTORICAL", as_of)
    snapshot_ranks(memory, "OOS", bars[-1]["as_of_time"])
    rebuild_projections(memory, bars)
    live_decide(memory)
    attach_counterfactuals(memory, bars)
    return memory


def possible_rsi_space_size() -> int:
    return 49
