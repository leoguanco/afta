# ✨ Feature Specification: Object Tracking (Vision Worker)

> **Context:** This spec is part of the [Football Intelligence Engine](../feature_specs.md) project. For infrastructure constraints (TDD, Hexagonal Architecture, GPU Workers), see [../01_infrastructure/01_infrastructure_spec.md](../01_infrastructure/01_infrastructure_spec.md).

## 1. 🚀 Overview & Motivation

- **Feature Name:** Vision Engine Worker
- **Goal:** Accurately detect and track players from video files using deep learning, running as an asynchronous background worker.
- **Problem Solved (The "Why"):** Tracking moves computer vision data into the Domain. This is a heavy computational task that must be decoupled from the API.
- **Scope:**
  - **In Scope:** YOLOv8 + ByteTrack pipeline, Celery/RabbitMQ Worker, Domain Event publication (`TrackingCompleted`).
  - **Out of Scope:** Real-time visualization (handled by specific review tools).

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **System**, I want **tracking to happen in the background**, so that **the API doesn't time out.**

| Criteria ID | Acceptance Criteria                                                                    | Status |
| :---------- | :------------------------------------------------------------------------------------- | :----- |
| US1.1       | The system SHALL accept a video upload and return a `job_id` immediately.              | [x]    |
| US1.2       | The Vision Worker SHALL process the video and save results to the Tracking Repository. | [x]    |

### **User Story 2:** As a **Domain**, I want **clean Trajectory objects**, so that **I don't depend on YOLO internals.**

| Criteria ID | Acceptance Criteria                                                            | Status |
| :---------- | :----------------------------------------------------------------------------- | :----- |
| US2.1       | The Worker SHALL transform raw Bounding Boxes into `Trajectory` Value Objects. | [x]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture (Hexagonal)**

- **Infrastructure:**
  - `src/infrastructure/vision/yolo_detector.py`
  - `src/infrastructure/vision/byte_tracker.py`
  - `src/infrastructure/worker/celery_app.py`
- **Application:**
  - `src/application/use_cases/process_video.py`
- **Domain:**
  - `src/domain/events/video_processed.py`

### **3.2 Implementation Steps**

1.  **Worker Setup:** Configure Celery with Redis.
2.  **Vision Pipeline:** Wrap YOLOv8 in a class that implements a generic `ObjectDetector` interface.
3.  **Result Storage:** Save parquet files to Object Storage (MinIO) and metadata to DB.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - **GPU Isolation:** The Worker container is the _only_ place needing NVIDIA drivers.
- **Edge Cases:**
  - **Video Corrupt:** Update Job Status to `FAILED` and log error.

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** Integration Testing.
- **Key Test Scenarios:**
  - **Scenario 1:** Submit a short validation clip -> Check DB for `COMPLETED` status after N seconds.

---

## 6. 🔗 References and Related Documentation

- [Celery Documentation](https://docs.celeryq.dev/en/stable/)
