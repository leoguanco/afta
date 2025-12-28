# ✨ Feature Specification: Ingestion Persistence (PostgreSQL)

## 1. 🚀 Overview & Motivation

- **Feature Name:** Ingestion Database Persistence
- **Goal:** Save normalized match events and metadata to PostgreSQL.
- **Problem Solved (The "Why"):** The ingestion worker currently fetches data but stops at a "TODO" comment. We need to persist this data to the relational DB to enable querying.
- **Scope:**
  - **In Scope:** `PostgresMatchRepo` implementation, SQLAlchemy models for `Match` and `Event`.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Backend API**, I want **matches in the DB**, so that **I can serve them to the UI.**

| Criteria ID | Acceptance Criteria                                                                   | Status |
| :---------- | :------------------------------------------------------------------------------------ | :----- |
| US1.1       | The system SHALL save the `Match` aggregate (and all `Event` entities) to PostgreSQL. | [ ]    |
| US1.2       | The operation SHALL be transactional (all or nothing).                                | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture and Dependencies**

- **Affected Components:**
  - `src/infrastructure/worker/tasks/ingestion_tasks.py` (Implement TODO)
  - `src/infrastructure/db/repositories/postgres_match_repo.py` (New)
  - `src/infrastructure/db/models.py` (SQLAlchemy models)
- **New Dependencies:** None (SQLAlchemy already exists).

### **3.2 Implementation Steps (High-Level)**

1.  **Database Models:** Ensure `MatchModel` and `EventModel` exist and map to domain entities.
2.  **Repository:** Implement `PostgresMatchRepo.save(match)`.
    - Use `session.add(model_instance)`.
    - Map Domain Entity -> DB Model.
3.  **Task Integration:** Instantiate repo in `ingestion_tasks.py` and call `.save()`.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - **Idempotency:** Re-ingesting the same match_id should overlap/update, or fail gracefully (prevent duplicates).
- **Edge Cases:**
  - **DB Connection Lost:** Celery auto-retry handles this.

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** Integration test with test DB.
- **Key Test Scenarios:**
  - **Scenario 1:** Ingest Match -> Query DB `SELECT count(*) FROM events WHERE match_id=...` -> Should be > 0.
