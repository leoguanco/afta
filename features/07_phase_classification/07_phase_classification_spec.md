# ✨ Feature Specification: Game Phase Classification

> **Context:** This spec is part of the [Football Intelligence Engine](../feature_specs.md) project. For infrastructure constraints (TDD, Hexagonal Architecture, Async Workers), see [../01_infrastructure/01_infrastructure_spec.md](../01_infrastructure/01_infrastructure_spec.md).

## 1. 🚀 Overview & Motivation

- **Feature Name:** Game Phase Classification (ML Engine)
- **Goal:** Automatically classify each moment of a match into one of four tactical phases based on player positions and ball location.
- **Problem Solved (The "Why"):** Tactical analysis requires understanding WHEN events happen in context. A pass during "organized attack" has different meaning than during "transition". Currently, analysts must manually segment video, which is time-consuming and subjective. This feature enables automatic segmentation.
- **Scope:**
  - **In Scope:** Classification into 4 phases (Organized Attack, Organized Defense, Attack→Defense Transition, Defense→Attack Transition), ML model training pipeline, inference per frame.
  - **Out of Scope:** Sub-phase classification (e.g., build-up vs. finishing), real-time inference.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Tactical Analyst**, I want **automatic phase labels for each frame**, so that **I can filter analysis by game context.**

| Criteria ID | Acceptance Criteria                                                                        | Status |
| :---------- | :----------------------------------------------------------------------------------------- | :----- |
| US1.1       | The system SHALL classify each tracking frame into one of 4 phases.                        | [ ]    |
| US1.2       | The classification SHALL use player positions, ball position, and recent movement vectors. | [ ]    |
| US1.3       | The system SHALL achieve >80% accuracy on labeled validation data.                         | [ ]    |

### **User Story 2:** As a **Data Scientist**, I want **to train phase models on labeled data**, so that **I can improve classification accuracy.**

| Criteria ID | Acceptance Criteria                                                     | Status |
| :---------- | :---------------------------------------------------------------------- | :----- |
| US2.1       | The system SHALL support training from labeled frame data (supervised). | [ ]    |
| US2.2       | The system SHALL persist trained models to object storage.              | [ ]    |
| US2.3       | The system SHALL support model versioning and rollback.                 | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture (Hexagonal + Async)**

- **Domain Layer:**
  - `src/domain/value_objects/game_phase.py`: Phase enum (ORGANIZED_ATTACK, ORGANIZED_DEFENSE, TRANSITION_ATK_DEF, TRANSITION_DEF_ATK)
  - `src/domain/entities/phase_sequence.py`: Rich entity containing phase classification logic
  - `src/domain/ports/phase_classifier_port.py`: Interface for ML classifier
- **Infrastructure Layer:**
  - `src/infrastructure/ml/sklearn_phase_classifier.py`: Scikit-learn implementation
  - `src/infrastructure/ml/model_storage.py`: MinIO adapter for model persistence
  - `src/infrastructure/worker/tasks/phase_classification_tasks.py`: Async classification job
- **Application Layer:**
  - `src/application/use_cases/classify_match_phases.py`: Orchestrates phase classification

### **3.2 Implementation Steps**

1.  **Define Domain:** Create `GamePhase` enum and `PhaseSequence` entity.
2.  **Define Port:** Create `PhaseClassifierPort` interface.
3.  **Feature Extraction:** Extract features from tracking data (team centroids, spread, ball position, velocity vectors).
4.  **Train Model:** Use scikit-learn (RandomForest/XGBoost) on labeled Metrica sample data.
5.  **Inference Task:** Create Celery task to classify all frames of a match.
6.  **Persist Results:** Store phase labels per frame in database.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - Model training should complete in <10 minutes for sample dataset.
  - Inference should process 25fps match in <5 minutes.
- **Assumptions:**
  - Ball possession can be inferred from player-ball proximity.
  - Labeled training data is available (Metrica sample data with manual labels).
- **Edge Cases:**
  - **Ball out of play:** Classify as TRANSITION or null phase.
  - **Set pieces:** May require separate classification (future enhancement).
  - **Missing tracking data:** Use interpolation or skip frame.

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** TDD with unit tests for feature extraction, integration tests for full pipeline.
- **Key Test Scenarios:**
  - **Scenario 1:** Classify a known "organized attack" sequence → expect 100% ORGANIZED_ATTACK labels.
  - **Scenario 2:** Classify a possession change → expect TRANSITION labels at turnover moment.
  - **Scenario 3:** Validate F1 score >0.80 on held-out test set.

---

## 6. 🔗 References and Related Documentation

- [Friends of Tracking - Phases of Play](https://www.youtube.com/watch?v=VU4P5M9dmGE)
- [Metrica Sports Sample Data](https://github.com/metrica-sports/sample-data)
- [scikit-learn RandomForest](https://scikit-learn.org/stable/modules/ensemble.html)
