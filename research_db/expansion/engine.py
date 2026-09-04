"""Phase 19-20 expansion registries. No ingest, no extra databases created."""
class ExpansionRegistry:
    def __init__(self) -> None:
        self.universes = [
            {"code": "CRYPTO_LAB_10", "phase": 19, "assets": 10, "years": 5, "ingested": False},
            {"code": "CRYPTO_FULL", "phase": 19, "assets": None, "years": None, "ingested": False},
        ]
        self.markets = [
            {"code": "US", "phase": 20, "horizon": "20-35y", "created": False},
            {"code": "CA", "phase": 20, "horizon": "20-35y", "created": False},
            {"code": "IN", "phase": 20, "horizon": "20-35y", "created": False},
        ]
    def ingested(self) -> bool:
        return any(u["ingested"] for u in self.universes) or any(m["created"] for m in self.markets)
