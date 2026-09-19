# Gate D — Agent runtime (design only)

Status: **DESIGN ONLY.** Requires trustworthy current state from Gates B–C.

## Goal

Connect Agent Ananta to this database **only** through:

- Phase 16 `interface.query_catalog`
- Phase 17 `interface.consult_event`

Read-only first. Every response carries `knowledge_time` and snapshot/run ids.  
Agent cannot write `research.*` or `market.*`. Policy/risk stays outside the LLM.

Allowed first queries: `current_regime`, `current_market_state`, `members_as_of`, `events_as_of`, `measurement_current`, `hypothesis_current_status`.

Out of scope: Mongo bypass, UI scraping, mutation, TAKE execution, autonomy grant.
