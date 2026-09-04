# Phase 8 — Grouping identity and temporal membership

Approved slice only. No aggregation, group engines, ops.current_group_*, ingest, or vendor taxonomy.

Objects: `research.market_group`, `research.group_membership`.
Query: `members_as_of(group, event_time, knowledge_time)`.
