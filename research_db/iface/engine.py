"""Phase 16 read-only query catalog. No agent runtime, no mutation."""
ALLOWED = {"current_regime", "current_market_state", "members_as_of", "events_as_of", "measurement_current", "hypothesis_current_status"}
class InterfaceDenied(PermissionError):
    pass
class QueryCatalog:
    def __init__(self) -> None:
        self.queries = sorted(ALLOWED)
    def request(self, name: str) -> str:
        if name not in ALLOWED:
            raise InterfaceDenied(f"query not on the agent catalog: {name}")
        return name
