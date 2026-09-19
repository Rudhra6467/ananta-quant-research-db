"""Phase 8 grouping identity and temporal membership."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from research_db.models.base import Base


class MarketGroup(Base):
    __tablename__ = "market_group"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class GroupMembership(Base):
    __tablename__ = "group_membership"
    __table_args__ = (
        CheckConstraint("expiry_time IS NULL OR expiry_time >= effective_time", name="ck_membership_interval"),
        CheckConstraint("member_group_id IS NULL OR member_group_id <> group_id", name="ck_no_self_member"),
        {"schema": "research"},
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.market_group.id"), nullable=False)
    member_kind: Mapped[str] = mapped_column(Text, nullable=False)
    member_instrument_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ref.instrument.id"))
    member_asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ref.asset.id"))
    member_group_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("research.market_group.id"))
    effective_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expiry_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    knowledge_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
