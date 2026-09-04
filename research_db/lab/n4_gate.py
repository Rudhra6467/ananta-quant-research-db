"""N4 execution wall."""
class N4Denied(PermissionError):
    pass
N4_EXECUTION_AUTHORIZED = False
def execute_n4(*_a, **_k):
    raise N4Denied("N4 blocked: design-only; requires accepted N3 + written grant")
