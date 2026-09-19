"""Persist Phase 8 group identity and membership facts."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from research_db.group.engine import GroupingEngine
from research_db.persist.ids import stable_id

ROOT = Path(__file__).resolve().parents[2]
PHASE8_DDL = ROOT / "sql" / "008_phase8_sqlite_twin.sql"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def install_phase8(self) -> None:
    self.conn.executescript(PHASE8_DDL.read_text(encoding="utf-8"))
    self.conn.commit()


def _ensure_eth(self, now: str) -> None:
    if "eth" not in self.ids:
        self.ids["eth"] = stable_id("asset", "ETH")
        self.ids["eth_instrument"] = stable_id("instrument", "FIXTURE", "ETH-USD-SPOT", "spot")
        self._upsert("ref__asset", {"id": self.ids["eth"], "symbol": "ETH", "name": "Ether", "asset_class": "crypto", "created_at": now})
        self._upsert(
            "ref__instrument",
            {
                "id": self.ids["eth_instrument"],
                "venue_id": self.ids["venue"],
                "base_asset_id": self.ids["eth"],
                "quote_asset_id": self.ids["usd"],
                "symbol": "ETH-USD-SPOT",
                "kind": "spot",
                "created_at": now,
            },
        )


def persist_groups(self, engine: GroupingEngine) -> dict[str, int]:
    now = _now()
    _ensure_eth(self, now)
    with self.conn:
        self._upsert(
            "ops__schema_gate",
            {
                "id": stable_id("gate", "phase8"),
                "phase": "phase8",
                "approved": 1,
                "ingestion_enabled": 0,
                "notes": "Grouping identity and temporal membership only",
                "created_at": now,
            },
        )
        for g in engine.groups:
            gid = stable_id("group", g["code"])
            self.ids[f"group:{g['code']}"] = gid
            self._upsert(
                "research__market_group",
                {"id": gid, "code": g["code"], "name": g["name"], "kind": g["kind"], "created_at": now},
            )
        for i, m in enumerate(engine.memberships):
            mid = stable_id("gmem", m["group"], m["member_kind"], m["member"], m["knowledge_time"], m.get("expiry_time") or "open", str(i))
            inst = asset = gref = None
            if m["member_kind"] == "instrument":
                inst = self.ids["eth_instrument"] if m["member"].startswith("ETH") else self.ids["instrument"]
            elif m["member_kind"] == "asset":
                asset = self.ids["eth"] if m["member"] == "ETH" else self.ids["btc"]
            else:
                gref = self.ids[f"group:{m['member']}"]
            self.conn.execute(
                """INSERT OR IGNORE INTO research__group_membership
                   (id, group_id, member_kind, member_instrument_id, member_asset_id,
                    member_group_id, member_code, effective_time, expiry_time,
                    knowledge_time, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    mid,
                    self.ids[f"group:{m['group']}"],
                    m["member_kind"],
                    inst,
                    asset,
                    gref,
                    m["member"],
                    m["effective_time"],
                    m.get("expiry_time"),
                    m["knowledge_time"],
                    now,
                ),
            )
    return {
        "groups": self._count("research__market_group"),
        "memberships": self._count("research__group_membership"),
    }


def members_as_of(self, group_code: str, event_time: str, knowledge_time: str, member_kind: str | None = None) -> list[str]:
    gid = self.ids.get(f"group:{group_code}") or self.conn.execute(
        "SELECT id FROM research__market_group WHERE code = ?", (group_code,)
    ).fetchone()["id"]
    rows = self.conn.execute(
        """SELECT member_kind, member_code, effective_time, expiry_time, knowledge_time
           FROM research__group_membership
           WHERE group_id = ? AND knowledge_time <= ?
           ORDER BY knowledge_time ASC""",
        (gid, knowledge_time),
    ).fetchall()
    latest = {}
    for r in rows:
        latest[(r["member_kind"], r["member_code"])] = r
    out = []
    for r in latest.values():
        if member_kind and r["member_kind"] != member_kind:
            continue
        if r["effective_time"] > event_time:
            continue
        if r["expiry_time"] is not None and r["expiry_time"] <= event_time:
            continue
        out.append(r["member_code"])
    return sorted(out)


def bind(store_cls) -> None:
    store_cls.install_phase8 = install_phase8
    store_cls.persist_groups = persist_groups
    store_cls.members_as_of = members_as_of
