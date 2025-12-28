# ✨ Feature Specification: Pattern Detection & Clustering

> **Context:** This spec is part of the [Football Intelligence Engine](../feature_specs.md) project. For infrastructure constraints (TDD, Hexagonal Architecture, Async Workers), see [../01_infrastructure/01_infrastructure_spec.md](../01_infrastructure/01_infrastructure_spec.md).

## 1. 🚀 Overview & Motivation

- **Feature Name:** Tactical Pattern Detection (ML Clustering)
- **Goal:** Automatically identify recurring tactical patterns in a team's play (e.g., "build-up through right flank", "high press recovery") using unsupervised machine learning.
- **Problem Solved (The "Why"):** Coaches want to understand "How do we typically attack?" or "What patterns does the opponent repeat?". Manual video review is time-consuming. Clustering similar sequences reveals the team's tactical DNA and opponent tendencies.
- **Scope:**
  - **In Scope:** Sequence extraction, feature engineering, K-means/DBSCAN clustering, pattern labeling.
  - **Out of Scope:** Real-time pattern matching, cross-match pattern comparison (v2).

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Tactical Analyst**, I want **to discover repeating attack patterns**, so that **I can understand team tendencies.**

| Criteria ID | Acceptance Criteria                                                      | Status |
| :---------- | :----------------------------------------------------------------------- | :----- |
| US1.1       | The system SHALL extract possession sequences from tracking data.        | [ ]    |
| US1.2       | The system SHALL cluster similar sequences using unsupervised learning.  | [ ]    |
| US1.3       | Each cluster SHALL be labeled with a human-readable pattern description. | [ ]    |

### **User Story 2:** As a **Coach**, I want **pattern statistics per match**, so that **I can see which patterns we use most.**

| Criteria ID | Acceptance Criteria                                                        | Status |
| :---------- | :------------------------------------------------------------------------- | :----- |
| US2.1       | The system SHALL count occurrences of each pattern per match.              | [ ]    |
| US2.2       | The system SHALL calculate success rate for each pattern (xT gain, shots). | [ ]    |

### **User Story 3:** As an **Analyst**, I want **example sequences for each pattern**, so that **I can review them in video.**

| Criteria ID | Acceptance Criteria                                                           | Status |
| :---------- | :---------------------------------------------------------------------------- | :----- |
| US3.1       | The system SHALL store representative sequences (centroids) for each cluster. | [ ]    |
| US3.2       | The system SHALL provide timestamp ranges for pattern occurrences.            | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture (Hexagonal + Async)**

- **Domain Layer:**
  - `src/domain/entities/possession_sequence.py`: Rich entity for a sequence of events/positions
  - `src/domain/entities/tactical_pattern.py`: Rich entity representing a discovered pattern
  - `src/domain/value_objects/sequence_features.py`: Feature vector for a sequence
  - `src/domain/ports/pattern_detector_port.py`: Interface for pattern detection
- **Infrastructure Layer:**
  - `src/infrastructure/ml/sklearn_pattern_detector.py`: K-means/DBSCAN implementation
  - `src/infrastructure/worker/tasks/pattern_detection_tasks.py`: Async detection job
- **Application Layer:**
  - `src/application/use_cases/detect_patterns.py`: Orchestrates pattern detection

### **3.2 Implementation Steps**

1.  **Sequence Extraction:** Segment match into possession sequences (turnover to turnover).
2.  **Feature Engineering:** Extract features per sequence:
    - Start/end zone
    - Number of passes
    - Duration
    - xT progression
    - Player involvement pattern
    - Directional flow (left/right/center)
3.  **Clustering:** Apply K-means or DBSCAN to find natural groupings.
4.  **Labeling:** Use rule-based heuristics or LLM to name clusters (e.g., "Right wing build-up").
5.  **Statistics:** Calculate per-pattern metrics (count, success rate, avg xT).
6.  **Persistence:** Store patterns and assignments in database.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - Clustering should use deterministic seeding for reproducibility.
  - Pattern detection should complete in <2 minutes per match.
- **Assumptions:**
  - A "possession sequence" is defined as ball control between turnovers.
  - Minimum sequence length: 3 events.
- **Edge Cases:**
  - **Very short sequences (<3 events):** Exclude from clustering.
  - **Single-pattern match:** Handle gracefully (no clusters found).
  - **Outlier sequences:** DBSCAN naturally handles these.

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** TDD with unit tests for feature extraction, validation against known patterns.
- **Key Test Scenarios:**
  - **Scenario 1:** Extract sequences from sample match → verify count matches expected.
  - **Scenario 2:** Cluster similar sequences → verify they are grouped together.
  - **Scenario 3:** Validate silhouette score >0.3 for meaningful clusters.

---

## 6. 🔗 References and Related Documentation

- [Friends of Tracking - Clustering Passing Sequences](https://www.youtube.com/watch?v=AZ40wXo4LSI)
- [scikit-learn Clustering](https://scikit-learn.org/stable/modules/clustering.html)
- [Expected Threat (xT) Paper](https://karun.in/blog/expected-threat.html)
