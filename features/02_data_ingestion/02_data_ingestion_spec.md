# ✨ Feature Specification: Data Ingestion

> **Context:** This spec is part of the [Football Intelligence Engine](../feature_specs.md) project. For infrastructure constraints (TDD, Hexagonal Architecture, Async Workers), see [../01_infrastructure/01_infrastructure_spec.md](../01_infrastructure/01_infrastructure_spec.md).

## 1. 🚀 Overview & Motivation

- **Feature Name:** Data Ingestion (Async Hexagonal Adapter)
- **Goal:** Create a unified pipeline to load, clean, and normalize football data from various sources (StatsBomb, Metrica, Video Tracking) using asynchronous background workers.
- **Problem Solved (The "Why"):** different data providers use different coordinates (StatsBomb 120x80, Metrica 0-1) and formats (JSON, CSV). To keep our Domain Logic pure, we need an Anti-Corruption Layer (ACL) that translates external data into our internal Domain Entities (105x68m Metric Pitch).
- **Scope:**
  - **In Scope:** StatsBomb Adapter (JSON), Metrica Adapter (CSV), Internal Tracking Adapter (Parquet), Normalization Service, Async Task Queue Integration.
  - **Out of Scope:** Real-time stream ingestion (batch processing only).

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Developer**, I want **Async Ingestion Jobs**, so that **the API remains responsive during large data imports.**

| Criteria ID | Acceptance Criteria                                                                                   | Status |
| :---------- | :---------------------------------------------------------------------------------------------------- | :----- |
| US1.1       | The system SHALL accept an ingestion request and return a `job_id` immediately.                       | [ ]    |
| US1.2       | The ingestion task SHALL run in a background worker (e.g., Celery) to avoid blocking the main thread. | [ ]    |

### **User Story 2:** As a **Data Scientist**, I want **Standardized Coordinates**, so that **my analysis works for any league.**

| Criteria ID | Acceptance Criteria                                                                                                                          | Status |
| :---------- | :------------------------------------------------------------------------------------------------------------------------------------------- | :----- |
| US2.1       | All ingested data SHALL be transformed to the **Metric Pitch (105m x 68m)** Value Object.                                                    | [ ]    |
| US2.2       | StatsBomb coordinates (0-120, 0-80) SHALL be linearly scaled to (0-105, 0-68).                                                               | [ ]    |
| US2.3       | Metrica coordinates (0-1, 0-1) SHALL be linearly scaled to (0-105, 0-68).                                                                    | [ ]    |
| US2.4       | The system SHALL store events in the `match_events` table with a standard schema using a standardized `event_type` enum (Pass, Shot, Carry). | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture (Hexagonal + Async)**

- **Domain Layer:**
  - `src/domain/entities/match.py`: Root Aggregation.
  - `src/domain/entities/event.py`: Value Object for events (Pass, Shot).
  - `src/domain/ports/match_repository.py`: Interface for fetching raw data.
- **Infrastructure Layer:**
  - `src/infrastructure/adapters/statsbomb_adapter.py`: Implements `MatchRepository` using `statsbombpy`.
  - `src/infrastructure/adapters/metrica_adapter.py`: Implements `MatchRepository` using `pandas` for CSVs.
  - `src/infrastructure/worker/tasks/ingestion_tasks.py`: Celery tasks.
- **Application Layer:**
  - `src/application/use_cases/start_ingestion.py`: Orchestrates the async job.

### **3.2 Implementation Steps**

1.  **Define Domain Entities:** Create `Match`, `Event`, and `TrackingFrame` classes.
2.  **Define Ports:** Structure the `MatchRepository` abstract base class.
3.  **Implement StatsBomb Adapter:** Fetch data from `statsbombpy` and map it to `Match` entities.
4.  **Implement Metrica Adapter:** Parse CSV files and map to `Trajectory` entities.
5.  **Data Normalization:** Implement `CoordinateTransform` service to handle the scaling math.
6.  **TDD Tests:** Write tests for the `NormalizationService` (unit) and the `StatsBombAdapter` (integration).

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - **Memory Efficiency:** Use chunked processing (Polars/Pandas) for large tracking files.
- **Assumptions:**
  - The standard pitch size is always assumed to be 105m x 68m unless metadata specifies otherwise.
- **Edge Cases & Error Handling:**
  - **Missing Data:** Fill gaps in tracking data with interpolation (handled in Cleaning phase).
  - **External API Down:** Implementation of retry logic with exponential backoff in the background task.

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** Unit Tests for logic, Integration Tests for external adapters.
- **Key Test Scenarios:**
  - **Scenario 1:** Transform StatsBomb Center (60, 40) -> Metric Center (52.5, 34).
  - **Scenario 2:** Trigger an ingestion job and poll for the "COMPLETED" status.

---

## 6. 🔗 References and Related Documentation

- [StatsBomb Open Data](https://github.com/statsbomb/open-data)
- [Metrica Sports Sample Data](https://github.com/metrica-sports/sample-data)
