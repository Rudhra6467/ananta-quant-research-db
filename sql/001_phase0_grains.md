# Phase 0 table grains

Authoritative ORM: `research_db/models/phase0.py`  
Authoritative migration: `alembic/versions/0001_phase0_foundation.py`

| Table | Schema | Grain / key | Mutability |
| --- | --- | --- | --- |
| data_source, venue, asset, instrument, timeframe, market_universe | ref | stable identity codes | slowly changing |
| dataset_snapshot, ingestion_run, canonicalization_run | ops | one run / frozen extract | append |
| schema_gate | ops | one row per phase | gated updates |
| indicator_definition, feature_definition, feature_version | research | family / version | append versions |
| parameter_definition, parameter_set | research | exact signature per feature version | append |
| relationship_definition + relationship_term | research | versioned claim + ordered terms | append versions |
| experiment_run, experiment_trial | research | campaign run / one candidate evaluation | append |
| relationship_evidence | research | one evidence atom; may supersede | append-only |
| ranking_snapshot | research | relationship × stage × scoring model × as_of | append-only |
| decision_event | research | one ENTER/WAIT/SKIP at as_of | append-only |
| counterfactual_outcome | research | decision × path × horizon | append-only |
| relationship_current_summary | analytics | one current row per relationship | rebuildable |
| current_market_state | ops | instrument × venue × timeframe | upsert projection |
| current_feature_value | ops | feature_version × parameter_set × instrument × timeframe | upsert projection |
| current_regime_state | ops | instrument × timeframe × regime_family | upsert projection |
| operational_relationship_applicability | ops | relationship × context bucket | upsert projection |

No `feature_observation` hypertable in Phase 0. That table is Phase 2, and only for requested observations.
