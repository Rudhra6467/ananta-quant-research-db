# Gate E — Paper trading (design only)

Status: **DESIGN ONLY.** Requires Gate D auditability.

## Goal

Use `research.operating_profile` and `research.paper_decision` against real laboratory state.

- SAFE / AVERAGE / AGGRESSIVE
- `live_capital = false`, `capital = 0`
- SAFE cannot TAKE until a later explicit relaxation
- No venue adapter until a separate approval
- SKIP / WAIT remain first-class outcomes
- Evaluate both (A) strategy/engine edge and (B) whether the Agent improved decisions

Paper is aggressive experimentation; conclusions stay skeptical.
