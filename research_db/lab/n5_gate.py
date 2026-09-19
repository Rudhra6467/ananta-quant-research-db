"""N5 execution wall."""
class N5Denied(PermissionError):
    pass
N5_EXECUTION_AUTHORIZED = False
def execute_n5(*_a, **_k):
    raise N5Denied("N5 blocked: design-only; Agent runtime not granted")
