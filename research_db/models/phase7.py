"""Phase 7 measurement contracts. Current view is analytics-only."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from research_db.models.base import Base


def _pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def _ts() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class MeasurementFamily(Base):
    __tablename__ = "measurement_family"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _ts()


class MeasurementDefinition(Base):
    __tablename__ = "measurement_definition"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    family_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.measurement_family.id"), nullable=False)
    param_schema: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = _ts()


class MeasurementRequest(Base):
    __tablename__ = "measurement_request"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    definition_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.measurement_definition.id"), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _ts()


class MeasurementObservation(Base):
    __tablename__ = "measurement_observation"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    definition_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.measurement_definition.id"), nullable=False)
    relationship_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("research.relationship_definition.id"))
    hypothesis_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("research.hypothesis.id"))
    point_value: Mapped[float | None] = mapped_column(Numeric)
    sample_size: Mapped[int | None] = mapped_column(Integer)
    epistemic_status: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_direction: Mapped[str | None] = mapped_column(Text)
    condition_digest: Mapped[str] = mapped_column(Text, nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    knowledge_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = _ts()
