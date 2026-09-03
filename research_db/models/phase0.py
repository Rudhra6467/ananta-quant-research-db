"""Phase 0 tables. Grain is locked; most tables stay empty until later phases."""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Numeric, Text, UniqueConstraint, text
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
    __table_args__ = (UniqueConstraint("asset_class", "symbol", name="uq_asset_class_symbol"), {"schema": "ref"})
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

class Timeframe(Base):
    __tablename__ = "timeframe"
    __table_args__ = {"schema": "ref"}
    id: Mapped[uuid.UUID] = _pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = _ts()

class MarketUniverse(Base):
    __tablename__ = "market_universe"
    __table_args__ = {"schema": "ref"}
    id: Mapped[uuid.UUID] = _pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _ts()

class DatasetSnapshot(Base):
    __tablename__ = "dataset_snapshot"
    __table_args__ = {"schema": "ops"}
    id: Mapped[uuid.UUID] = _pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    data_source_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ref.data_source.id"))
    as_of_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = _ts()

class IngestionRun(Base):
    __tablename__ = "ingestion_run"
    __table_args__ = {"schema": "ops"}
    id: Mapped[uuid.UUID] = _pk()
    dataset_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ops.dataset_snapshot.id"))
    status: Mapped[str] = mapped_column(Text, nullable=False, default="planned")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = _ts()

class CanonicalizationRun(Base):
    __tablename__ = "canonicalization_run"
    __table_args__ = {"schema": "ops"}
    id: Mapped[uuid.UUID] = _pk()
    ingestion_run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ops.ingestion_run.id"))
    version: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="planned")
    created_at: Mapped[datetime] = _ts()

class SchemaGate(Base):
    __tablename__ = "schema_gate"
    __table_args__ = {"schema": "ops"}
    id: Mapped[uuid.UUID] = _pk()
    phase: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ingestion_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = _ts()

class IndicatorDefinition(Base):
    __tablename__ = "indicator_definition"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    family_code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _ts()

class FeatureDefinition(Base):
    __tablename__ = "feature_definition"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    indicator_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("research.indicator_definition.id"))
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _ts()

class FeatureVersion(Base):
    __tablename__ = "feature_version"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    feature_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.feature_definition.id"), nullable=False)
    version: Mapped[str] = mapped_column(Text, nullable=False)
    formula_ref: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = _ts()

class ParameterDefinition(Base):
    __tablename__ = "parameter_definition"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    feature_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.feature_definition.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    topology: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = _ts()

class ParameterSet(Base):
    __tablename__ = "parameter_set"
    __table_args__ = (UniqueConstraint("feature_version_id", "signature", name="uq_parameter_set_sig"), {"schema": "research"})
    id: Mapped[uuid.UUID] = _pk()
    feature_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.feature_version.id"), nullable=False)
    signature: Mapped[str] = mapped_column(Text, nullable=False)
    values: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = _ts()

class OutcomeDefinition(Base):
    __tablename__ = "outcome_definition"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    horizon_bars: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = _ts()

class ValidationStage(Base):
    __tablename__ = "validation_stage"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = _ts()

class RelationshipDefinition(Base):
    __tablename__ = "relationship_definition"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    version: Mapped[str] = mapped_column(Text, nullable=False, default="v1")
    outcome_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("research.outcome_definition.id"))
    expression: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = _ts()

class RelationshipTerm(Base):
    __tablename__ = "relationship_term"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    relationship_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.relationship_definition.id"), nullable=False)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)
    predicate: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = _ts()

class ExperimentRun(Base):
    __tablename__ = "experiment_run"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    dataset_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ops.dataset_snapshot.id"))
    code_commit: Mapped[str | None] = mapped_column(Text)
    config_hash: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="planned")
    created_at: Mapped[datetime] = _ts()

class ExperimentTrial(Base):
    __tablename__ = "experiment_trial"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    experiment_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.experiment_run.id"), nullable=False)
    relationship_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("research.relationship_definition.id"))
    parameter_set_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("research.parameter_set.id"))
    instrument_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ref.instrument.id"))
    timeframe_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ref.timeframe.id"))
    status: Mapped[str] = mapped_column(Text, nullable=False, default="queued")
    skip_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = _ts()

class RelationshipEvidence(Base):
    __tablename__ = "relationship_evidence"
    __table_args__ = (CheckConstraint("direction in ('untested','supports','contradicts','inconclusive','invalidated','decayed')", name="evidence_direction"), {"schema": "research"})
    id: Mapped[uuid.UUID] = _pk()
    relationship_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.relationship_definition.id"), nullable=False)
    trial_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("research.experiment_trial.id"))
    validation_stage_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("research.validation_stage.id"))
    direction: Mapped[str] = mapped_column(Text, nullable=False)
    sample_size: Mapped[int | None] = mapped_column(BigInteger)
    effect: Mapped[float | None] = mapped_column(Numeric)
    uncertainty: Mapped[float | None] = mapped_column(Numeric)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    supersedes_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("research.relationship_evidence.id"))
    created_at: Mapped[datetime] = _ts()

class RankingSnapshot(Base):
    __tablename__ = "ranking_snapshot"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    relationship_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.relationship_definition.id"), nullable=False)
    validation_stage_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.validation_stage.id"), nullable=False)
    scoring_model_version: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float | None] = mapped_column(Numeric)
    rank: Mapped[int | None] = mapped_column(Integer)
    population_size: Mapped[int | None] = mapped_column(Integer)
    cohort_label: Mapped[str | None] = mapped_column(Text)
    as_of_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = _ts()

class DecisionEvent(Base):
    __tablename__ = "decision_event"
    __table_args__ = (CheckConstraint("action in ('ENTER','WAIT','SKIP')", name="decision_action"), {"schema": "research"})
    id: Mapped[uuid.UUID] = _pk()
    instrument_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ref.instrument.id"))
    timeframe_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ref.timeframe.id"))
    relationship_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("research.relationship_definition.id"))
    action: Mapped[str] = mapped_column(Text, nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    as_of_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    state_version: Mapped[str | None] = mapped_column(Text)
    policy_version: Mapped[str | None] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text)
    context: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = _ts()

class CounterfactualOutcome(Base):
    __tablename__ = "counterfactual_outcome"
    __table_args__ = {"schema": "research"}
    id: Mapped[uuid.UUID] = _pk()
    decision_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.decision_event.id"), nullable=False)
    action_path: Mapped[str] = mapped_column(Text, nullable=False)
    horizon_bars: Mapped[int] = mapped_column(Integer, nullable=False)
    realized_return: Mapped[float | None] = mapped_column(Numeric)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = _ts()

class RelationshipCurrentSummary(Base):
    __tablename__ = "relationship_current_summary"
    __table_args__ = {"schema": "analytics"}
    relationship_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.relationship_definition.id"), primary_key=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="research_only")
    blended_score: Mapped[float | None] = mapped_column(Numeric)
    confidence: Mapped[float | None] = mapped_column(Numeric)
    current_rank: Mapped[int | None] = mapped_column(Integer)
    scoring_model_version: Mapped[str] = mapped_column(Text, nullable=False)
    source_watermark: Mapped[str | None] = mapped_column(Text)
    computed_at: Mapped[datetime] = _ts()

class CurrentMarketState(Base):
    __tablename__ = "current_market_state"
    __table_args__ = (UniqueConstraint("instrument_id", "venue_id", "timeframe_id", name="uq_current_market_state"), {"schema": "ops"})
    id: Mapped[uuid.UUID] = _pk()
    instrument_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.instrument.id"), nullable=False)
    venue_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.venue.id"), nullable=False)
    timeframe_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.timeframe.id"), nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    as_of_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    state_version: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    updated_at: Mapped[datetime] = _ts()

class CurrentFeatureValue(Base):
    __tablename__ = "current_feature_value"
    __table_args__ = (UniqueConstraint("feature_version_id", "parameter_set_id", "instrument_id", "timeframe_id", name="uq_current_feature_value"), {"schema": "ops"})
    id: Mapped[uuid.UUID] = _pk()
    feature_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.feature_version.id"), nullable=False)
    parameter_set_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.parameter_set.id"), nullable=False)
    instrument_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.instrument.id"), nullable=False)
    timeframe_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.timeframe.id"), nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    as_of_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    value: Mapped[float | None] = mapped_column(Numeric)
    updated_at: Mapped[datetime] = _ts()

class CurrentRegimeState(Base):
    __tablename__ = "current_regime_state"
    __table_args__ = (UniqueConstraint("instrument_id", "timeframe_id", "regime_family", name="uq_current_regime"), {"schema": "ops"})
    id: Mapped[uuid.UUID] = _pk()
    instrument_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.instrument.id"), nullable=False)
    timeframe_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ref.timeframe.id"), nullable=False)
    regime_family: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Numeric)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    as_of_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    provenance: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    updated_at: Mapped[datetime] = _ts()

class OperationalRelationshipApplicability(Base):
    __tablename__ = "operational_relationship_applicability"
    __table_args__ = {"schema": "ops"}
    id: Mapped[uuid.UUID] = _pk()
    relationship_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research.relationship_definition.id"), nullable=False)
    instrument_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ref.instrument.id"))
    timeframe_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ref.timeframe.id"))
    regime_bucket: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rank: Mapped[int | None] = mapped_column(Integer)
    score: Mapped[float | None] = mapped_column(Numeric)
    state_version: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = _ts()
