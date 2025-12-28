# ✨ Feature Specification: Tactical Metrics Engine

> **Context:** This spec is part of the [Football Intelligence Engine](../../feature_specs.md) project. For infrastructure constraints (TDD, Domain Purity, Async Workers), see [../01_infrastructure/01_infrastructure_spec.md](../01_infrastructure/01_infrastructure_spec.md).

## 1. 🚀 Overview & Motivation

- **Feature Name:** Tactical Domain Model (Async Engine)
- **Goal:** High-performance calculation of tactical metrics (Pitch Control, xG, PPDA, Physical Load) using background processing.
- **Problem Solved (The "Why"):** Calculating complex models like Pitch Control for every frame of a 90-minute match (~135,000 frames) is a "heavy" task. Coordinates alone don't tell the story; we need to quantify "Space Control" and "Pressure".
- **Scope:**
  - **In Scope:** `PitchControlService` (Spearman), `PhysicalMetricsService` (Speed/Distance), `ExpectedThreatService` (xT), `PressureService` (PPDA), Async Worker Integration.
  - **Out of Scope:** Biomechanics, Injury prediction.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Physical Trainer**, I want **Distance & Speed**, so that **I can manage player load.**

| Criteria ID | Acceptance Criteria                                                                                                  | Status |
| :---------- | :------------------------------------------------------------------------------------------------------------------- | :----- |
| US1.1       | The system SHALL calculate **Total Distance (km)**, **Max Speed (km/h)**, and **Sprints (>25km/h)** for each player. | [x]    |
| US1.2       | The background worker SHALL smooth velocity data (Savitzky-Golay filter) to remove noise.                            | [x]    |

### **User Story 2:** As a **Tactical Analyst**, I want **Pitch Control**, so that **I can visualize space domination.**

| Criteria ID | Acceptance Criteria                                                                                                | Status |
| :---------- | :----------------------------------------------------------------------------------------------------------------- | :----- |
| US2.1       | The system SHALL compute a **Pitch Control** model (based on Spearman 2018) for every frame.                       | [x]    |
| US2.2       | The output SHALL be a Probability Grid (e.g., 32x24) representing the likelihood of ball control at each location. | [x]    |

### **User Story 3:** As an **Analyst**, I want **metrics to be pre-calculated**, so that **the dashboard is fast.**

| Criteria ID | Acceptance Criteria                                                                         | Status |
| :---------- | :------------------------------------------------------------------------------------------ | :----- |
| US3.1       | The system SHALL trigger metric calculation jobs automatically after tracking is completed. | [x]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture (Hexagonal + Async/Worker)**

- **Domain Layer:**
  - `src/domain/entities/match_frame.py`: Rich entity containing Pitch Control logic.
  - `src/domain/entities/player_trajectory.py`: Rich entity containing Physics/Velocity logic.
  - `src/domain/entities/tactical_match.py`: Rich entity containing PPDA/Event logic.
- **Infrastructure Layer:**
  - `src/infrastructure/worker/tasks/metrics_tasks.py`: Background workers that invoke domain services.
  - `src/infrastructure/storage/metrics_repo.py`: Persistence for pre-calculated grids (Parquet/Binary).

### **3.2 Implementation Steps**

1.  **Physical Engine:** Implement `PlayerTrajectory.calculate_physical_metrics()` to compute velocity and distance.
2.  **Space Engine:** Implement `MatchFrame.calculate_pitch_control()` using vectorized numpy operations.
3.  **Tactical Engine:** Implement `TacticalMatch.calculate_ppda()` for defensive pressure.
4.  **Async Workers:** Celery tasks that process chunks of match frames in parallel.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - **Vectorization:** Must use `numpy` to ensure the background task completes match-level processing in minutes.
  - **Pure Domain:** The domain logic must not depend on the Database or API.
  - **Scientific primitives:** `numpy` is permitted in the domain layer as it is treated as a fundamental scientific primitive for this specific vectorized domain logic.
- **Edge Cases:**
  - **Substitute Players:** Metrics must be aggregated by Player ID to handle substitutions correctly.
  - **Outliers:** Speed > 36km/h should be flagged or clipped.

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** Unit tests for math, Performance tests for throughput.
- **Key Test Scenarios:**
  - **Scenario 1:** A player moving at constant 1 m/frame (at 25fps) should have speed = 25m/s.
  - **Scenario 2:** Verify that Convex Hull area decreases when players cluster together.

---

## 6. 🔗 References and Related Documentation

- [Spearman 2018 (Beyond Expected Goals)](https://www.search-vi.co.uk/fileadmin/Analysis_Data/Spearman_Beyond_Expected_Goals.pdf)
