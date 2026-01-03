# 📋 Implementation Plan: Event Recognition Engine

> **Spec:** [10_event_recognition_spec.md](10_event_recognition_spec.md)

---

## Phase 1: Tracking Stabilization (Prerequisite)

### 1.1 Trajectory Smoother

#### [NEW] `src/domain/services/trajectory_smoother.py`

- Implement `TrajectorySmoother` class
- Apply Savitzky-Golay filter to (x, y) coordinates
- Parameters: `window_size=5`, `poly_order=2`

#### [MODIFY] `src/infrastructure/worker/tasks/vision_tasks.py`

- After ByteTrack output, apply `TrajectorySmoother`
- Pass smoothed trajectories to metrics task

---

### 1.2 Track Cleaning

#### [NEW] `src/domain/services/track_cleaner.py`

- Implement `TrackCleaner` class
- Remove tracks with duration < 0.5 seconds (ghost filtering)
- Merge fragmented tracks using spatial proximity

#### [MODIFY] `src/infrastructure/worker/tasks/vision_tasks.py`

- Apply `TrackCleaner` after smoothing, before saving

---

## Phase 2: Heuristic Event Detection

### 2.1 Event Detector

#### [NEW] `src/domain/entities/inferred_event.py`

- Add `InferredEvent` dataclass
- Add new `EventType` values: `POSSESSION`, `PASS_ATTEMPT`, etc.

#### [NEW] `src/application/use_cases/event_detector.py`

- Implement `HeuristicEventDetector`
- State machine: `None -> Possession(P) -> Pass -> Possession(Q)`
- Detect: Possession, Pass, Pressure

#### [MODIFY] `src/application/use_cases/metrics_calculator.py`

- Call `HeuristicEventDetector` if `event_data` is empty
- Use inferred events for PPDA calculation

---

## Verification Plan

1. **Unit Tests:**

   - `test_trajectory_smoother.py`: Assert velocity spikes are reduced
   - `test_track_cleaner.py`: Assert ghost tracks removed
   - `test_event_detector.py`: Assert passes detected from synthetic data

2. **Integration Test:**
   - Process test video, verify PPDA > 0 (not inf)
