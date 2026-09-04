# Gate C — Shift / event research (design only)

Status: **DESIGN ONLY.** Requires a Gate B tape.

## Goal

Exercise Phase 11 objects on real bars, then — only if that representation holds — research detection.

Sequence:

1. Human or research annotation of candidate onsets/peaks (same grain as `E_BREAK_T20` / `E_SHIFT_T24`).
2. Pre / event / post windows relative to local volatility and liquidity, not a 10% rule.
3. Context links to regime, group, and bars knowable at T.
4. Analogue pairs without treating similarity scores as truth.
5. Keep false positives and failed detectors as negative knowledge.

CUSUM / PELT / BOCPD are candidate *engines*, not replacements for event identity.  
OOS required before any detector is called operational. Detection ≠ prediction ≠ rank.
