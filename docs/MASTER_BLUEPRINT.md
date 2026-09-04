# Ananta Database — Constitution + Master Blueprint

Status: Canonical governing brief. 2026-09-04.
Three layers: Constitution (invariants) | Destination roadmap | Current command.
A future item is not permission to implement it.

## Purpose
Time-aware, provenance-preserving, evidence-oriented market memory — not a price warehouse.
Loop: Observe → Validate → Preserve → Derive → Measure → Detect State → Detect Change → Compare → Test → Learn → Expose Evidence → Agent Reasoning → Outcome → New Evidence.
Laboratory first: ~5 years, ~10 crypto assets. Database ≠ Agent.

## Invariants
- Identity ≠ market fact ≠ observation ≠ measurement ≠ evidence ≠ hypothesis ≠ prediction ≠ rank ≠ projection.
- event/effective time ≠ knowledge time. No lookahead. News/AI about T after T is not contemporaneous knowledge.
- Append-only evidence. Reset = new run, not DELETE.
- Live path reads only `ops.current_*`.
- Requested materialization only. No Cartesian cubes. No vendor-owned ontology.
- Observation → association → hypothesis → test → OOS. Correlation ≠ causation.
- Compound identity `(asset_class, symbol)`. Lineage graph and conformal prediction surfaces reserved.
- `INGESTION_ENABLED=false` until an ingest phase is approved.

## Grouping (P8 approved slice)
Hierarchy via relationships: market → asset class → sector/category → group → asset → instrument.
Distinguish: group exists; member assigned; membership known/effective; derived group observation.
Membership is market-world knowledge. Group state is derived.
`members_as_of(group, T)` uses effective/expiry + knowledge_time ≤ T.

## Memory tiering (later)
0–12y high-resolution rolling window (not deletion). Older = compressed + raw archive. Important old events stay rich.

## Shift/event intelligence (later)
Not a fixed 10% rule. Relative to distribution/vol/liquidity/regime.
normal → early anomaly → break/onset → major shift → post-shift → new regime.
Windows T−N…T+N. Context + cross group/sector/market. Analogues tested, failures kept.

## Reliability
Correctness → PIT → reproducibility → scientific validity → scale.
Postgres 16 + Timescale in production; SQLite twin in CI. Incremental watermarks. Bounded ops cadence.
Security review is a gate before Agent. Agent is read/retrieve, not free mutation.

## Roadmap (repo reality)
| Phase | Intent | Status |
| --- | --- | --- |
| 0–7 | Foundation through requested measurements | COMPLETE / FROZEN |
| 8 | Group identity + temporal membership + members_as_of | APPROVED next |
| 9 | Richer requested features | direction |
| 10 | Deeper versioned state/regime | direction |
| 11 | Event / structural-change intelligence | direction |
| 12 | Cross-asset/group/market relationships | direction |
| 13 | Event memory + analogues | direction |
| 14 | Memory compression | direction |
| 15 | Security / architecture gate | direction |
| 16 | Agent DB interface | direction |
| 17 | Agent integration | direction |
| 18 | Paper Safe/Average/Aggressive | direction |
| 19 | Full crypto scale | direction |
| 20 | Separate multi-market DBs | direction |

Future numbers may be split or reordered after review.

## Current command
P7 frozen. Next code = P8 slice only. No aggregation, group engines, shifts, ingest, agent, or P2–P7 redesign.
