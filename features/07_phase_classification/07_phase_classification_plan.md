# Phase Classification Implementation Plan

This plan details the implementation of the Game Phase Classification feature as specified in `07_phase_classification_spec.md`. The goal is to automatically classify match frames into 4 tactical phases using ML.

## User Review Required

> [!IMPORTANT] > **ML Model Selection**: Using RandomForest as baseline. Can be upgraded to XGBoost or neural network after initial validation.

## Implementation Status

- [ ] Domain Layer (value objects, entities, ports)
- [ ] Feature Extraction
- [ ] Infrastructure Layer (ML adapter, Celery task)
- [ ] Application Layer (use case)
- [ ] API Endpoints
- [ ] Tests

## Proposed Changes

### Domain Layer

#### [NEW] [game_phase.py](../../backend/src/domain/value_objects/game_phase.py)

- Implement `GamePhase` enum.
- Values: `ORGANIZED_ATTACK`, `ORGANIZED_DEFENSE`, `TRANSITION_ATK_DEF`, `TRANSITION_DEF_ATK`, `UNKNOWN`.

#### [NEW] [phase_features.py](../../backend/src/domain/value_objects/phase_features.py)

- Implement `PhaseFeatures` value object.
- **Features**: Team centroids, spread, ball position, velocity, defensive line.

#### [NEW] [phase_sequence.py](../../backend/src/domain/entities/phase_sequence.py)

- Implement `PhaseSequence` Rich Entity.
- **Methods**: `get_phase_at_frame()`, `calculate_phase_transitions()`.

#### [NEW] [phase_classifier_port.py](../../backend/src/domain/ports/phase_classifier_port.py)

- Define `PhaseClassifierPort` interface.
- **Methods**: `classify()`, `train()`.

---

### Infrastructure Layer

#### [NEW] [sklearn_phase_classifier.py](../../backend/src/infrastructure/ml/sklearn_phase_classifier.py)

- Implement `SklearnPhaseClassifier` adapter.
- **Model**: RandomForest with 100 estimators.
- **Methods**: `classify()`, `train()`, `save_model()`, `load_model()`.

#### [NEW] [model_storage.py](../../backend/src/infrastructure/ml/model_storage.py)

- Implement model persistence to MinIO.
- **Methods**: `save_model()`, `load_model()`, `list_versions()`.

#### [NEW] [phase_classification_tasks.py](../../backend/src/infrastructure/worker/tasks/phase_classification_tasks.py)

- Implement Celery task `classify_match_phases_task`.
- **Flow**: Load tracking → Extract features → Classify → Store results.

---

### Application Layer

#### [NEW] [classify_match_phases.py](../../backend/src/application/use_cases/classify_match_phases.py)

- Implement `ClassifyMatchPhasesUseCase`.
- **Dependencies**: `PhaseClassifierPort`, `ObjectStoragePort`.

---

### API Endpoints

#### [MODIFY] [main.py](../../backend/src/infrastructure/api/main.py)

- Add `POST /api/v1/matches/{id}/classify-phases`.
- Add `GET /api/v1/matches/{id}/phases`.

---

## Verification Plan

### Automated Tests

```bash
# Run tests
pytest backend/tests/domain/value_objects/test_game_phase.py
pytest backend/tests/domain/entities/test_phase_sequence.py
pytest backend/tests/infrastructure/ml/test_sklearn_phase_classifier.py
```

### Manual Verification

1. **Load sample Metrica data** with known phases.
2. **Run classification task** via API.
3. **Verify phase labels** match expected values.
4. **Check accuracy** ≥80% on validation set.

---

## New Test Files

- `tests/domain/value_objects/test_game_phase.py`
- `tests/domain/entities/test_phase_sequence.py`
- `tests/infrastructure/ml/test_sklearn_phase_classifier.py`
