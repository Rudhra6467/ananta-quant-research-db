"""Phase 15 access and mutation policy. Not an agent."""
ROLES = {"ingest_writer", "research_writer", "live_reader", "admin", "agent_reader"}
class AccessDenied(PermissionError):
    pass
class AccessPolicy:
    def __init__(self) -> None:
        self.grants = [
            {"role": "live_reader", "surface": "ops.current_*", "action": "read"},
            {"role": "research_writer", "surface": "research.*", "action": "append"},
            {"role": "research_writer", "surface": "market.*", "action": "read"},
            {"role": "agent_reader", "surface": "interface.*", "action": "read"},
            {"role": "admin", "surface": "research.*", "action": "admin"},
        ]
        self.forbidden = [
            {"role": "agent_reader", "surface": "research.*", "action": "write"},
            {"role": "agent_reader", "surface": "market.*", "action": "write"},
            {"role": "live_reader", "surface": "research.*", "action": "read"},
        ]
    def allows(self, role: str, surface: str, action: str) -> bool:
        if role not in ROLES:
            raise AccessDenied(f"unknown role {role}")
        if any(f["role"] == role and f["surface"] == surface and f["action"] == action for f in self.forbidden):
            return False
        return any(g["role"] == role and g["surface"] == surface and g["action"] == action for g in self.grants)
