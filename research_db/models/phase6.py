"""Phase 6 hypothesis contracts. Current status is an analytics projection."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from research_db.models.base import Base


def _pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def _ts() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Hypothesis(Base):
    __tablename__ = "hypothesis"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    relationship_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.relationship_definition.id"), nullable=False)
    claim_kind: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _ts()


class HypothesisStatusEvent(Base):
    __tablename__ = "hypothesis_status_event"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    hypothesis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.hypothesis.id"), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    knowledge_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    evidence_direction: Mapped[str | None] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = _ts()


class HypothesisSupportLink(Base):
    __tablename__ = "hypothesis_support_link"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    hypothesis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.hypothesis.id"), nullable=False)
    source_kind: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[str] = mapped_column(Text, nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    knowledge_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = _ts()


class AnalogueDefinition(Base):
    __tablename__ = "analogue_definition"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    version: Mapped[str] = mapped_column(Text, nullable=False)
    metric_name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _ts()


class HypothesisCurrentStatus(Base):
    __tablename__ = "hypothesis_current_status"
    __table_args__ = {"schema": "analytics"}
    hypothesis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.hypothesis.id"), primary_key=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    knowledge_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    computed_at: Mapped[datetime] = _ts()
