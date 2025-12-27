# Tactical Metrics Implementation Plan

This plan details the implementation of the Tactical Domain Model as specified in `specs/tactical_metrics_spec.md`. The goal is to provide high-performance calculation of tactical metrics (Pitch Control, xG, PPDA, Physical Load) using background processing.

## User Review Required

> [!IMPORTANT] > **Dependency on `numpy`**: The spec now explicitly permits `numpy` as a scientific primitive in the Domain Layer, treating it as an extension of the language for vectorization purposes. This aligns with the "Pure Domain" constraint by standardizing it as a core type.

## Implementation Status

- [x] Domain Entities (`match_frame.py`, `player_trajectory.py`, `tactical_match.py`)
- [x] Infrastructure (`metrics_repo.py`, `metrics_tasks.py`)
- [x] Tests (`test_tactical_metrics.py`)

✅ All files implemented and ready for testing.

## Proposed Changes

### Domain Layer

Implementation of core mathematical models and tactical logic.

#### [NEW] [match_frame.py](../../backend/src/domain/entities/match_frame.py)

- Implement `MatchFrame` Rich Entity.
- **Methods**: `calculate_pitch_control()`.
- **Logic**: Spearman 2018 algorithm (embedded).

#### [NEW] [player_trajectory.py](../../backend/src/domain/entities/player_trajectory.py)

- Implement `PlayerTrajectory` Rich Entity.
- **Methods**: `calculate_physical_metrics()`.
- **Logic**: Velocity smoothing, sprint detection.

#### [NEW] [tactical_match.py](../../backend/src/domain/entities/tactical_match.py)

- Implement `TacticalMatch` Rich Entity.
- **Methods**: `calculate_ppda()`.

### Infrastructure Layer

Integration with background workers and persistence.

#### [NEW] [metrics_repo.py](../../backend/src/infrastructure/storage/metrics_repo.py)

- Implement `MetricsRepository`.
- **Storage**: Save calculated grids/metrics (Parquet or Binary Blob via Database).
- **Interface**: `save_pitch_control_frame`, `save_physical_stats`.

#### [NEW] [metrics_tasks.py](../../backend/src/infrastructure/worker/tasks/metrics_tasks.py)

- Implement Celery tasks.
- **Tasks**: `calculate_match_metrics_task`.
- **Flow**: Fetch match data -> Invoke Domain Services -> Save results via Repository.

## Verification Plan

### Automated Tests

Run unit tests for the new domain services.

```bash
# Run new tests (to be created)
pytest backend/tests/domain/test_tactical_metrics.py
```

### Manual Verification

1.  **Trigger Calculation**:
    - Manually trigger the Celery task (or use a script/API endpoint if available) for a sample match.
2.  **Verify Logs**:
    - Check Celery worker logs for "Metrics calculation completed".
3.  **Check Output**:
    - Inspect the database/storage to ensure metrics are saved.

### New Tests

I will create a new test file `backend/tests/domain/test_tactical_metrics.py` covering:

- `PhysicsService`: Test velocity calculation with known inputs (e.g., constant motion).
- `PitchControlService`: Test grid output shape and value range (0-1).
