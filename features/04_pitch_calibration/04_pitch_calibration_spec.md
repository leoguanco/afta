# ✨ Feature Specification: Pitch Calibration

> **Context:** This spec is part of the [Football Intelligence Engine](../feature_specs.md) project. For infrastructure constraints (TDD, Hexagonal Architecture, Async Processing), see [../01_infrastructure/01_infrastructure_spec.md](../01_infrastructure/01_infrastructure_spec.md).

## 1. 🚀 Overview & Motivation

- **Feature Name:** Pitch Normalization Service (Async)
- **Goal:** Create an automated (or manual fallback) service to calculate the Homography matrix asynchronously for match clips.
- **Problem Solved (The "Why"):** Automatic line detection and landmark matching can be computationally intensive when applied across many frames or clips. Offloading this to a background worker keeps the UI snappy.
- **Scope:**
  - **In Scope:** Homography calculation logic, Coordinate Mapper interface, Async Task wrapper.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **User**, I want **to start calibration and receive a notification**, so that **I don't have to wait on the screen.**

| Criteria ID | Acceptance Criteria                                                                      | Status |
| :---------- | :--------------------------------------------------------------------------------------- | :----- |
| US1.1       | The system SHALL process calibration requests in a background worker.                    | [x]    |
| US1.2       | The system SHALL notify the UI (via webhook or status poll) when $H$ matrices are ready. | [x]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture (Hexagonal + Async)**

- **Domain:**
  - `src/domain/entities/pitch_calibration.py` (Rich entity with homography calculation)
  - `src/domain/value_objects/keypoint.py` (Keypoint value object)
  - `src/domain/value_objects/homography_matrix.py` (Homography matrix value object)
  - `src/domain/ports/keypoint_detector.py` (Interface for keypoint detection)
- **Infrastructure:**
  - `src/infrastructure/cv/opencv_homography.py` (OpenCV implementation)
  - `src/infrastructure/worker/tasks/calibration_tasks.py` (Celery tasks)
- **Application:**
  - `src/application/use_cases/start_calibration.py` (Orchestrates async calibration)

### **3.2 Implementation Steps**

1.  **Define Port:** `KeypointDetector` port.
2.  **Rich Entity:** `PitchCalibration` entity encapsulates homography calculation logic.
3.  **Implement Async Logic:** Wrap the calibration logic in a background worker task.
4.  **Application Logic:** `StartCalibration(match_id)` use case returns a job identifier.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - Math logic should be unit testable.
- **Edge Cases:**
  - **No Lines Found:** Background task should flag the match for "Manual Calibration Required".

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** Integration Test for the async flow.
- **Key Test Scenarios:**
  - **Scenario 1:** Verify the background job stores the resulting Homography matrix in the DB.

---

## 6. 🔗 References and Related Documentation

- [OpenCV Homography](https://docs.opencv.org/4.x/d9/dab/tutorial_homography.html)
