"""Phase 0 tables. Grain is locked; most tables stay empty until later phases."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from research_db.models.base import Base


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def _pk():
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)


def _ts():
    return mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class DataSource(Base):
    __tablename__ = "data_source"
    __table_args__ = {"schema": "ref"}
    id: Mapped[uuid.UUID] = _pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _ts()


class Venue(Base):
    __tablename__ = "venue"
    __table_args__ = {"schema": "ref"}
    id: Mapped[uuid.UUID] = _pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _ts()


class Asset(Base):
    __tablename__ = "asset"
    __table_args__ = (
        UniqueConstraint("asset_class", "symbol", name="uq_asset_class_symbol"),
        {"schema": "ref"},
    )
    id: Mapped[uuid.UUID] = _pk()
    symbol: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    asset_class: Mapped[str] = mapped_column(Text, nullable=False, default="crypto")
    created_at: Mapped[datetime] = _ts()


class Instrument(Base):
    __tablename__ = "instrument"
    __table_args__ = {"schema": "ref"}
    id: Mapped[uuid.UUID] = _pk()
    venue_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.venue.id"), nullable=False)
    base_asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.asset.id"), nullable=False)
    quote_asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ref.asset.id"))
    symbol: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[str] = mapped_column(Text, nullable=False, default="spot")
    created_at: Mapped[datetime] = _ts()
