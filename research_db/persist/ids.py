from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

NS = uuid.uuid5(uuid.NAMESPACE_URL, "ananta-quant-research-db")


def stable_id(*parts: str) -> str:
    return str(uuid.uuid5(NS, "|".join(parts)))


def request_hash(spec: dict[str, Any]) -> str:
    blob = json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()
