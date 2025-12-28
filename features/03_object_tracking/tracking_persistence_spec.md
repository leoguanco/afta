# ✨ Feature Specification: Vision Persistence (Parquet + MinIO)

## 1. 🚀 Overview & Motivation

- **Feature Name:** Vision Persistence Layer
- **Goal:** Save heavy player trajectory data to object storage (MinIO) instead of dropping it.
- **Problem Solved (The "Why"):** Tracked coordinates are the core value of the vision pipeline. Currently, they are lost after processing (TODO in code). Database storage is too expensive/slow for high-frequency tracking data (25fps _ 22 players _ 90 mins). Parquet on MinIO is the standard for this data lake pattern.
- **Scope:**
  - **In Scope:** `MinIOAdapter`, `ObjectStoragePort`, Parquet serialization.
- **Out of Scope:** Database indexing of individual frames.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Data Engineer**, I want **efficient storage**, so that **I can query match metrics later.**

| Criteria ID | Acceptance Criteria                                                              | Status |
| :---------- | :------------------------------------------------------------------------------- | :----- |
| US1.1       | The system SHALL serialize `VideoProcessed` trajectories into a `.parquet` file. | [ ]    |
| US1.2       | The system SHALL upload the parquet file to MinIO bucket `tracking-data`.        | [ ]    |
| US1.3       | The system SHALL update the database with the `storage_path` of the file.        | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture and Dependencies**

- **Affected Components:**
  - `src/infrastructure/worker/tasks/vision_tasks.py` (Implement TODO)
  - `src/infrastructure/storage/minio_adapter.py` (New)
- **New Dependencies:**
  - `minio`: S3 compatible client.
  - `polars` or `pandas`: For Parquet writing.

### **3.2 Implementation Steps (High-Level)**

1.  **Define Port:** Create `ObjectStoragePort` (save/load file).
2.  **Implement Adapter:** Create `MinIOAdapter` using `minio` library.
3.  **Serialize:** In the task, convert `List[Trajectory]` to a DataFrame.
4.  **Save:** Upload to `tracking/{match_id}/trajectories.parquet`.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - **Buckets:** Ensure `tracking-data` bucket exists on startup.
- **Edge Cases:**
  - **MinIO Down:** Retry upload 3 times, then mark job as `FAILED`.

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** Integration test with local MinIO container.
- **Key Test Scenarios:**
  - **Scenario 1:** Process dummy video -> Check `http://localhost:9000` for file existence.
