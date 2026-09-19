"""Phase 8 grouping identity and temporal membership. No aggregation."""

from __future__ import annotations

from typing import Any

ALLOWED_KINDS = {"market", "asset_class", "sector", "category", "group"}
ALLOWED_MEMBER_KINDS = {"instrument", "asset", "group"}


class GroupDenied(PermissionError):
    pass


class GroupingEngine:
    def __init__(self) -> None:
        self.groups: list[dict[str, str]] = []
        self.memberships: list[dict[str, Any]] = []

    def define_group(self, code: str, name: str, kind: str) -> dict[str, str]:
        if kind not in ALLOWED_KINDS:
            raise GroupDenied(f"invalid group kind {kind}")
        if any(g["code"] == code for g in self.groups):
            raise GroupDenied(f"duplicate group identity {code}")
        row = {"code": code, "name": name, "kind": kind}
        self.groups.append(row)
        return row

    def assign(
        self,
        *,
        group: str,
        member_kind: str,
        member: str,
        effective_time: str,
        knowledge_time: str,
        expiry_time: str | None = None,
    ) -> dict[str, Any]:
        if member_kind not in ALLOWED_MEMBER_KINDS:
            raise GroupDenied(f"invalid member kind {member_kind}")
        if not any(g["code"] == group for g in self.groups):
            raise GroupDenied(f"unknown group {group}")
        if member_kind == "group":
            if not any(g["code"] == member for g in self.groups):
                raise GroupDenied(f"unknown member group {member}")
            if member == group:
                raise GroupDenied("group cannot be a member of itself")
        if expiry_time is not None and expiry_time < effective_time:
            raise GroupDenied("expiry_time precedes effective_time")
        row = {
            "group": group,
            "member_kind": member_kind,
            "member": member,
            "effective_time": effective_time,
            "expiry_time": expiry_time,
            "knowledge_time": knowledge_time,
        }
        self.memberships.append(row)
        return row

    def expire(self, group: str, member: str, expiry_time: str, knowledge_time: str) -> dict[str, Any]:
        open_rows = [
            m
            for m in self.memberships
            if m["group"] == group and m["member"] == member and m["expiry_time"] is None
        ]
        if not open_rows:
            raise GroupDenied(f"no open membership {group}/{member}")
        prior = open_rows[-1]
        closed = dict(prior)
        closed["expiry_time"] = expiry_time
        closed["knowledge_time"] = knowledge_time
        self.memberships.append(closed)
        return closed

    def members_as_of(
        self,
        group: str,
        event_time: str,
        knowledge_time: str,
        member_kind: str | None = None,
    ) -> list[dict[str, Any]]:
        latest: dict[tuple[str, str], dict[str, Any]] = {}
        for m in sorted(self.memberships, key=lambda row: row["knowledge_time"]):
            if m["group"] != group:
                continue
            if m["knowledge_time"] > knowledge_time:
                continue
            latest[(m["member_kind"], m["member"])] = m
        out = []
        for m in latest.values():
            if member_kind and m["member_kind"] != member_kind:
                continue
            if m["effective_time"] > event_time:
                continue
            if m["expiry_time"] is not None and m["expiry_time"] <= event_time:
                continue
            out.append(m)
        return sorted(out, key=lambda row: (row["member_kind"], row["member"]))


def fixture_grouping() -> GroupingEngine:
    g = GroupingEngine()
    g.define_group("MKT_CRYPTO", "Crypto market", "market")
    g.define_group("AC_CRYPTO_SPOT", "Crypto spot", "asset_class")
    g.define_group("SEC_LAYER1", "Layer-1 majors", "sector")
    g.define_group("GRP_MAJORS", "Major coins (lab)", "group")
    g.assign(group="MKT_CRYPTO", member_kind="group", member="AC_CRYPTO_SPOT",
             effective_time="2026-01-01T00:00:00+00:00", knowledge_time="2026-01-01T00:00:00+00:00")
    g.assign(group="AC_CRYPTO_SPOT", member_kind="group", member="SEC_LAYER1",
             effective_time="2026-01-01T00:00:00+00:00", knowledge_time="2026-01-01T00:00:00+00:00")
    g.assign(group="SEC_LAYER1", member_kind="group", member="GRP_MAJORS",
             effective_time="2026-01-01T00:00:00+00:00", knowledge_time="2026-01-01T00:00:00+00:00")
    g.assign(group="GRP_MAJORS", member_kind="instrument", member="BTC-USD-SPOT",
             effective_time="2026-01-01T00:00:00+00:00", knowledge_time="2026-01-01T12:00:00+00:00")
    g.assign(group="GRP_MAJORS", member_kind="asset", member="BTC",
             effective_time="2026-01-01T00:00:00+00:00", knowledge_time="2026-01-01T12:00:00+00:00")
    g.expire("GRP_MAJORS", "BTC-USD-SPOT", "2026-01-02T00:00:00+00:00", "2026-01-02T06:00:00+00:00")
    g.assign(group="GRP_MAJORS", member_kind="instrument", member="ETH-USD-SPOT",
             effective_time="2026-01-02T00:00:00+00:00", knowledge_time="2026-01-02T06:00:00+00:00")
    return g
