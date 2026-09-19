# Phase 8 — Grouping / hierarchy DESIGN

Status: **DESIGN ONLY**. Not implemented. Architecture locked.
Phase 7 is COMPLETE and frozen.

Grouping is part of market representation, not UI.

## Target resolution

```
market → asset class → sector/category → group → asset → instrument
```

An instrument may belong to many groups. Membership is time-dependent knowledge.

## Canonical answers

1. Group is a versioned identity in the market ontology, not a price fact.
2. Membership is a relationship fact: group ↔ asset|instrument|group, with effective/expiry + knowledge_time + source.
3. Hierarchy is parent/child group membership, not a single-parent column on asset.
4. Group observations/state/regime/relationships/experiments reuse P4–P7 with subject_kind=group.
5. Aggregation/drill-down are requested measurements over members as of T — no group×asset×TF×regime cube.
6. PIT: members_as_of(group, T) uses effective <= T, expiry null or > T, knowledge_time <= T.
7. Provenance on membership + existing snapshot/run on derived facts. Full graph is P12.
8. group_id may appear in P7 condition_digest / P9 predicates.

## Proposed objects (not created now)

| object | purpose | fact/projection | temporal | write | later |
| --- | --- | --- | --- | --- | --- |
| `ref.market_group` | identity + kind | definition | none | insert | all |
| `ref.market_group_edge` | parent → child group | fact-like validity | effective/expiry + knowledge_time | append | hierarchy |
| `ref.group_membership` | group ↔ member | **fact** | effective/expiry + knowledge_time | append | P7, P10 |
| `analytics.group_members_current` | current members | projection | watermark | replace | optional later ops |
| existing feature/state/regime/measurement | group-level derived | existing facts | existing clocks | requested only | P7, P10, P15 |

No `ops.current_group_*` unless later approved.

## First implementation slice (after approval)

Identity + membership facts + `members_as_of(T)` only.

Defer: group ranking, group prediction, auto aggregation engine, vendor taxonomy ingest, Cartesian scans.

## Risks

Single-parent sector column; prebuilt cubes; treating today's classification as historical fact.
