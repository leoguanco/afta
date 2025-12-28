# Pattern Detection Implementation Plan

This plan details the implementation of the Tactical Pattern Detection feature as specified in `09_pattern_detection_spec.md`. The goal is to discover recurring tactical patterns using unsupervised ML clustering.

## User Review Required

> [!IMPORTANT] > **Clustering Algorithm**: Starting with K-means (deterministic). DBSCAN available for noise-tolerant clustering.

> [!NOTE] > **Sequence Definition**: A possession sequence is defined as ball control between turnovers (minimum 3 events).

## Implementation Status

- [ ] Domain Layer (entities, value objects, ports)
- [ ] Sequence Extraction
- [ ] Feature Engineering
- [ ] ML Clustering Adapter
- [ ] Pattern Labeling
- [ ] Application Layer (use case)
- [ ] API Endpoints
- [ ] Tests

## Proposed Changes

### Domain Layer

#### [NEW] [possession_sequence.py](../../backend/src/domain/entities/possession_sequence.py)

- Implement `PossessionSequence` Rich Entity.
- **Methods**: `get_duration_seconds()`, `get_start_zone()`, `get_end_zone()`, `get_xt_progression()`.

#### [NEW] [tactical_pattern.py](../../backend/src/domain/entities/tactical_pattern.py)

- Implement `TacticalPattern` Rich Entity.
- **Fields**: `pattern_id`, `label`, `occurrence_count`, `success_rate`, `avg_xt_gain`.

#### [NEW] [sequence_features.py](../../backend/src/domain/value_objects/sequence_features.py)

- Implement `SequenceFeatures` value object.
- **Features**: Start/end zones, duration, event counts, xT progression.
- **Method**: `to_vector() -> np.ndarray`.

#### [NEW] [sequence_extractor.py](../../backend/src/domain/entities/sequence_extractor.py)

- Implement sequence extraction logic.
- **Method**: `extract(events, frames) -> List[PossessionSequence]`.

#### [NEW] [pattern_detector_port.py](../../backend/src/domain/ports/pattern_detector_port.py)

- Define `PatternDetectorPort` interface.
- **Methods**: `fit()`, `predict_cluster()`, `get_patterns()`.

#### [NEW] [pattern_repository.py](../../backend/src/domain/ports/pattern_repository.py)

- Define `PatternRepository` interface.
- **Methods**: `save_patterns()`, `get_patterns()`, `get_pattern_occurrences()`.

---

### Infrastructure Layer

#### [NEW] [sklearn_pattern_detector.py](../../backend/src/infrastructure/ml/sklearn_pattern_detector.py)

- Implement `SklearnPatternDetector` adapter.
- **Models**: K-means, DBSCAN.
- **Methods**: `fit()`, `_create_patterns()`.

#### [NEW] [pattern_labeler.py](../../backend/src/infrastructure/ml/pattern_labeler.py)

- Implement rule-based pattern labeling.
- **Method**: `label_pattern() -> str`.

#### [NEW] [postgres_pattern_repo.py](../../backend/src/infrastructure/db/repositories/postgres_pattern_repo.py)

- Implement pattern persistence.

#### [NEW] [pattern_detection_tasks.py](../../backend/src/infrastructure/worker/tasks/pattern_detection_tasks.py)

- Implement Celery task `detect_patterns_task`.
- **Flow**: Load data → Extract sequences → Compute features → Cluster → Label → Store.

---

### Application Layer

#### [NEW] [detect_patterns.py](../../backend/src/application/use_cases/detect_patterns.py)

- Implement `DetectPatternsUseCase`.
- **Dependencies**: `MatchRepository`, `PatternDetectorPort`, `PatternRepository`.

---

### API Endpoints

#### [NEW] [patterns.py](../../backend/src/infrastructure/api/endpoints/patterns.py)

- Add router for pattern endpoints.
- `POST /api/v1/patterns/detect` - Start pattern detection.
- `GET /api/v1/matches/{id}/patterns` - Get discovered patterns.
- `GET /api/v1/patterns/{id}/examples` - Get example sequences.

---

## Verification Plan

### Automated Tests

```bash
# Run tests
pytest backend/tests/domain/entities/test_possession_sequence.py
pytest backend/tests/domain/entities/test_tactical_pattern.py
pytest backend/tests/domain/entities/test_sequence_extractor.py
pytest backend/tests/infrastructure/ml/test_sklearn_pattern_detector.py
```

### Manual Verification

1. **Extract sequences** from Metrica sample → Verify count.
2. **Run clustering** → Check silhouette score ≥0.3.
3. **Review pattern labels** → Verify meaningful names.
4. **Check pattern statistics** → Validate counts and success rates.

---

## New Test Files

- `tests/domain/entities/test_possession_sequence.py`
- `tests/domain/entities/test_tactical_pattern.py`
- `tests/domain/entities/test_sequence_extractor.py`
- `tests/infrastructure/ml/test_sklearn_pattern_detector.py`
