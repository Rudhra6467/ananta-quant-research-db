"""Phase 17 catalog-only consult. Agent cannot mutate market/research facts."""
from __future__ import annotations
from typing import Any
from research_db.iface.engine import QueryCatalog
class AgentDenied(PermissionError):
    pass
class AgentConsult:
    def __init__(self) -> None:
        self.catalog = QueryCatalog()
        self.log = []
    def consult(self, query: str, knowledge_time: str, payload: dict[str, Any] | None = None):
        self.catalog.request(query)
        row = {"query": query, "knowledge_time": knowledge_time, "payload": payload or {}, "mutated": False}
        self.log.append(row)
        return row
    def mutate(self, *_a, **_k) -> None:
        raise AgentDenied("agent consult cannot mutate the database")
