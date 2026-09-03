"""Phase 2 grains. Product store is PostgreSQL 16 + TimescaleDB."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from research_db.models.base import Base


def _pk():
    return mapped_column(UUID(as_uuid=True), primary_key=True)


class RawMarketEvent(Base):
    __tablename__ = "market_event"
    __table_args__ = (
        UniqueConstraint("data_source_id", "source_record_id", name="uq_raw_source_record"),
        {"schema": "raw"},
    )
    id: Mapped[uuid.UUID] = _pk()
    data_source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.data_source.id"), nullable=False)
    source_record_id: Mapped[str] = mapped_column(Text, nullable=False)
    instrument_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.instrument.id"), nullable=False)
    timeframe_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.timeframe.id"), nullable=False)
    dataset_snapshot_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ops.dataset_snapshot.id"), nullable=False)
    ingestion_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ops.ingestion_run.id"), nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    knowledge_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    checksum: Mapped[str] = mapped_column(Text, nullable=False)


class OhlcvBar(Base):
    __tablename__ = "ohlcv_bar"
    __table_args__ = {"schema": "market"}
    id: Mapped[uuid.UUID] = _pk()
    instrument_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.instrument.id"), nullable=False)
    venue_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.venue.id"), nullable=False)
    timeframe_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.timeframe.id"), nullable=False)
    dataset_snapshot_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ops.dataset_snapshot.id"), nullable=False)
    raw_event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("raw.market_event.id"), nullable=False)
    canonicalization_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ops.canonicalization_run.id"), nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    knowledge_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    open: Mapped[float] = mapped_column(Numeric, nullable=False)
    high: Mapped[float] = mapped_column(Numeric, nullable=False)
    low: Mapped[float] = mapped_column(Numeric, nullable=False)
    close: Mapped[float] = mapped_column(Numeric, nullable=False)
    volume: Mapped[float] = mapped_column(Numeric, nullable=False)
    canonicalization_version: Mapped[str] = mapped_column(Text, nullable=False)


class FeatureObservation(Base):
    __tablename__ = "observation"
    __table_args__ = {"schema": "feature"}
    id: Mapped[uuid.UUID] = _pk()
    feature_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.feature_version.id"), nullable=False)
    parameter_set_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.parameter_set.id"), nullable=False)
    instrument_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.instrument.id"), nullable=False)
    timeframe_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.timeframe.id"), nullable=False)
    dataset_snapshot_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ops.dataset_snapshot.id"), nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    knowledge_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    value: Mapped[float] = mapped_column(Numeric, nullable=False)


class ParameterRegion(Base):
    __tablename__ = "parameter_region"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    feature_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.feature_definition.id"), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    dimension: Mapped[str] = mapped_column(Text, nullable=False)
    lo: Mapped[float] = mapped_column(Numeric, nullable=False)
    hi: Mapped[float] = mapped_column(Numeric, nullable=False)
    detection: Mapped[str] = mapped_column(Text, nullable=False)


class CombinationRequest(Base):
    __tablename__ = "combination_request"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    relationship_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("research.relationship_definition.id"))
    request_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    specification: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
