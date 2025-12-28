# ✨ Feature Specification: Ingestion Persistence Completion

## 1. 🚀 Overview & Motivation

- **Feature Name:** Ingestion Database Persistence Fix
- **Goal:** Complete the implementation of `PostgresMatchRepo` to correctly save normalized match events and metadata.
- **Problem Solved (The "Why"):** The current implementation contains `TODO`s where event reconstruction and metadata mapping should handle `StatsBomb` specific data structure. This effectively blocks full data persistence.
- **Scope:**
  - **In Scope:**
    - Full implementation of `PostgresMatchRepo.save()` and `get_match()`.
    - Reconstruction of `Event` entities from `EventModel`.
    - Proper metadata handling (removing hardcoded "statsbomb" source).

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Developer**, I want **reliable data persistence**, so that **no data is lost after ingestion.**

| Criteria ID | Acceptance Criteria                                                                                         | Status |
| :---------- | :---------------------------------------------------------------------------------------------------------- | :----- |
| US1.1       | `PostgresMatchRepo.save(match)` SHALL persist all events in `match.events`.                                 | [ ]    |
| US1.2       | `PostgresMatchRepo.get_match(id)` SHALL return a `Match` object with a populated `events` list (not empty). | [ ]    |
| US1.3       | The `source` field in `MatchModel` SHALL be derived from match metadata, not hardcoded.                     | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture and Dependencies**

- **Affected Components:**
  - `src/infrastructure/db/repositories/postgres_match_repo.py`

### **3.2 Implementation Steps**

1.  **Refactor `get_match`:**
    - Fetch `MatchModel` with `EventModel`s joined.
    - Iterate `EventModel`s and convert to `Event` domain objects using `Coordinates` value object.
2.  **Refactor `save`:**
    - Ensure transactionality.
    - Extract `source` from `match.metadata.get("source", "statsbomb")`.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - Adhere to Clean Architecture structure.
- **Edge Cases:**
  - Handle matches with 0 events gracefully.

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** Extend `test_postgres_match_repo.py`.
- **Key Test Scenarios:**
  - **Reconstruction:** Save a match with 10 events, load it, assert `len(match.events) == 10`.
