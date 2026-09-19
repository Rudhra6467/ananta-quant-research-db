"""Phase 5 state / regime contracts. Rebuildable current projections stay in ops."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from research_db.models.base import Base


def _pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def _ts() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class RegimeFamily(Base):
    __tablename__ = "regime_family"
    __table_args__ = {"schema": "state"}
    id: Mapped[uuid.UUID] = _pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _ts()


class MarketStateObservation(Base):
    __tablename__ = "market_state_observation"
    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "venue_id",
            "timeframe_id",
            "event_time",
            "knowledge_time",
            name="uq_market_state_observation",
        ),
        {"schema": "state"},
    )
    id: Mapped[uuid.UUID] = _pk()
    instrument_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.instrument.id"), nullable=False)
    venue_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.venue.id"), nullable=False)
    timeframe_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.timeframe.id"), nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    knowledge_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    close: Mapped[float] = mapped_column(Numeric, nullable=False)
    state_version: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _ts()


class RegimeObservation(Base):
    __tablename__ = "regime_observation"
    __table_args__ = (
        UniqueConstraint(
            "instrument_id",
            "timeframe_id",
            "regime_family",
            "event_time",
            "knowledge_time",
            name="uq_regime_observation",
        ),
        {"schema": "state"},
    )
    id: Mapped[uuid.UUID] = _pk()
    instrument_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.instrument.id"), nullable=False)
    timeframe_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.timeframe.id"), nullable=False)
    regime_family: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    value: Mapped[float | None] = mapped_column(Numeric)
    epistemic_status: Mapped[str] = mapped_column(Text, nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    knowledge_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    provenance: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = _ts()


class StateCompileWatermark(Base):
    __tablename__ = "state_compile_watermark"
    __table_args__ = {"schema": "ops"}
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    last_event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_regime_label: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = _ts()
