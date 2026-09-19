"""Phase 10 versioned regime definitions. Does not replace Phase 5 compiler."""

from __future__ import annotations

from typing import Any


class RegimeDefinitionRegistry:
    def __init__(self) -> None:
        self.definitions: list[dict[str, Any]] = [
            {
                "code": "rsi_region",
                "version": "v1",
                "family": "rsi_region",
                "rules": {"oversold_lt": 35.0, "else": "neutral", "insufficient": "UNKNOWN"},
                "status": "active",
            }
        ]

    def active(self, family: str) -> dict[str, Any]:
        matches = [d for d in self.definitions if d["family"] == family and d["status"] == "active"]
        if not matches:
            raise KeyError(family)
        return matches[-1]
