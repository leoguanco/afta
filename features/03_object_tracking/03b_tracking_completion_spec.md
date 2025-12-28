# ✨ Feature Specification: Tracking Persistence Completion

## 1. 🚀 Overview & Motivation

- **Feature Name:** Tracking Persistence (MinIO) Completion
- **Goal:** Verify and harden the `MinIOAdapter` logic to ensure large parquet files are reliably uploaded.
- **Problem Solved (The "Why"):** Use of `MinIO` for tracking data is theoretically implemented but lacks robust error handling and verification against the real `vision_tasks.py` workflow.
- **Scope:**
  - **In Scope:** `MinIOAdapter` hardening, `process_video_task` retry logic.
  - **Out of Scope:** Database schema changes.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **System**, I want **robust file uploads**, so that **network blips don't lose data.**

| Criteria ID | Acceptance Criteria                                                                               | Status |
| :---------- | :------------------------------------------------------------------------------------------------ | :----- |
| US1.1       | `process_video_task` SHALL retry uploads to MinIO at least 2 times before failing.                | [ ]    |
| US1.2       | `MinIOAdapter` SHALL verify bucket existence before every upload attempt (or cache exact status). | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture and Dependencies**

- **Affected Components:**
  - `src/infrastructure/storage/minio_adapter.py`
  - `src/infrastructure/worker/tasks/vision_tasks.py`

### **3.2 Implementation Steps**

1.  **Hardening:**
    - Add `try/except` blocks specifically for `S3Error` in `vision_tasks.py`.
    - Ensure `MinIOAdapter` sets `content_type` correctly to `application/octet-stream` or `application/x-parquet`.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - MinIO container reference `minio:9000` inside Docker network.

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** Integration test simulating network failure (mock).
