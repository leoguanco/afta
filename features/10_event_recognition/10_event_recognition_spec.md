# ✨ Feature Specification: Event Recognition Engine

## 1. 🚀 Overview & Motivation

- **Feature Name:** Event Recognition Engine
- **Goal:** Automatically infer semantic match events (Pass, Shot, Possession, Pressure) from raw video tracking data, effectively "simulating" StatsBomb-like event data.
- **Problem Solved:** Raw video tracking provides _where_ players are (x, y), but not _what_ they are doing. To calculate advanced metrics like PPDA, xG, or Possession %, we need discrete events.
- **Scope:**
  - **Phase 1 (Heuristic):** Rule-based inference using player-ball proximity and velocity vectors.
  - **Phase 2 (AI):** Deep Learning-based Action Recognition (e.g., SlowFast, VideoMAE) for complex events (Tackles, Fouls).

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As an **Analyst**, I want **Possession Detection**, so that I can analyze team dominance.

| Criteria ID | Acceptance Criteria                                                                    | Status |
| :---------- | :------------------------------------------------------------------------------------- | :----- |
| US1.1       | System SHALL assign "Possession" to a player if Ball is within `1.5m` for `>3` frames. | [ ]    |
| US1.2       | System SHALL detect "Loss of Possession" when the controlling team changes.            | [ ]    |
| US1.3       | System SHALL calculate Possession % per team based on aggregated possession frames.    | [ ]    |

### **User Story 2:** As an **Analyst**, I want **Pass Detection**, so that I can visualize passing networks.

| Criteria ID | Acceptance Criteria                                                                                | Status |
| :---------- | :------------------------------------------------------------------------------------------------- | :----- |
| US2.1       | System SHALL detect a "Pass" when possession transfers from Player A to Player B of the same team. | [ ]    |
| US2.2       | System SHALL record `start_x`, `start_y`, `end_x`, `end_y` for each pass.                          | [ ]    |
| US2.3       | System SHALL calculate Pass Velocity to distinguish passes from dribbles.                          | [ ]    |

### **User Story 3:** As an **Analyst**, I want **Pressure Detection**, so that I can calculate PPDA.

| Criteria ID | Acceptance Criteria                                                                                                    | Status |
| :---------- | :--------------------------------------------------------------------------------------------------------------------- | :----- |
| US3.1       | System SHALL detect "Pressure" when a defending player enters a `2m` radius of the ball carrier with velocity `>3m/s`. | [ ]    |
| US3.2       | System SHALL aggregate pressure events to enable PPDA calculation for video uploads.                                   | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture (Hybrid Approach)**

We will implement a **Hybrid Event Engine** within the Application Layer:

1.  **`TrajectorySmoother` (Prerequisite):**

    - **Why?** Raw tracking data is noisy ("shaky").
    - **Fix:** Apply **Savitzky-Golay Filter** or **Kalman Filter** to smooth (x, y) coordinates before event detection. Eliminates "900 players" (ghosts) and "exceptional velocity" (noise).

2.  **`HeuristicEventDetector` (Phase 1):**

    - Iterates through smoothed frames.
    - Maintains a state machine: `None` -> `Possession(Player A)` -> `Pass(In Flight)` -> `Possession(Player B)`.

3.  **`ActionRecognitionModel` (Phase 2 - Future):**
    - Python-based inference using a pre-trained VideoMAE model.
    - Runs on short 64-frame crops around the ball.

### **3.2 Domain Model Updates**

```python
class EventType(Enum):
    POSSESSION = "possession"
    PASS_ATTEMPT = "pass_attempt"
    PASS_COMPLETE = "pass_complete"
    PRESSURE = "pressure"

@dataclass
class InferredEvent:
    frame_start: int
    frame_end: int
    event_type: EventType
    actors: List[str]  # e.g., [passer_id, receiver_id]
    location: Tuple[float, float]
```

### **3.3 Stabilization Fixes (Addressing "Flakiness")**

Before detection, we must fix the input quality:

1.  **Track Cleaning:**
    - Remove "ghost" tracks (duration < 0.5s).
    - Merge fragmented tracks (Re-ID: if Player X disappears and Player Y appears close by with similar histogram -> Match).
2.  **Velocity Smoothing:**
    - Instead of `v = (p2 - p1) / dt`, use smoothed derivatives to prevent velocity spikes.

---

## 4. 🧪 Testing & Validation Plan

- **Unit Tests:**
  - Create synthetic tracking scenarios (e.g., "Player A moves to (10,10), Ball moves A->B").
  - Assert `HeuristicEventDetector` outputs correct `PASS_COMPLETE` event.
- **Integration Tests:**
  - Run full pipeline on `test_video.mp4`.
  - Verify generated JSON events correlate with visual reality.
