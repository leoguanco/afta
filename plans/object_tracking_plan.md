# Implementation Plan: Object Tracking Feature

## Goal

Implement the **Object Tracking (Vision Worker)** module as defined in [object_tracking_spec.md](../specs/object_tracking_spec.md), strictly adhering to the [infrastructure_spec.md](../specs/infrastructure_spec.md) constraints.

---

## User Review Required

> [!IMPORTANT] > **GPU Isolation:** This worker runs ONLY in the `worker-gpu` container with NVIDIA CUDA access. Tasks are routed to `gpu_queue`.

> [!WARNING] > **Domain Purity:** The `Trajectory` Value Object in `domain/` will NOT import YOLO or OpenCV. Only stdlib types.

---

## Proposed Changes

### Domain Layer (`backend/src/domain/`)

| File                                  | Purpose                                                                    |
| :------------------------------------ | :------------------------------------------------------------------------- |
| [NEW] `value_objects/trajectory.py`   | Immutable `Trajectory` dataclass (frame_id, object_id, x, y, object_type). |
| [NEW] `value_objects/bounding_box.py` | `BoundingBox` dataclass (x1, y1, x2, y2, confidence, class_id).            |
| [NEW] `events/tracking_completed.py`  | Domain Event published when a video is fully processed.                    |
| [NEW] `ports/object_detector.py`      | Abstract interface for detection (implemented by YOLO adapter).            |
| [NEW] `ports/object_tracker.py`       | Abstract interface for tracking (implemented by ByteTrack adapter).        |

---

### Infrastructure Layer (`backend/src/infrastructure/`)

#### Vision Pipeline

| File                              | Purpose                                                             |
| :-------------------------------- | :------------------------------------------------------------------ |
| [NEW] `vision/yolo_detector.py`   | Adapter implementing `ObjectDetector` using YOLOv8.                 |
| [NEW] `vision/byte_tracker.py`    | Adapter implementing `ObjectTracker` using ByteTrack.               |
| [NEW] `vision/video_processor.py` | Orchestrator that reads video frames, runs detection, and tracking. |

#### Storage

| File                               | Purpose                                                        |
| :--------------------------------- | :------------------------------------------------------------- |
| [NEW] `storage/trajectory_repo.py` | Saves `Trajectory` data to MinIO (Parquet) and metadata to DB. |

#### Worker

| File                                 | Purpose                                                               |
| :----------------------------------- | :-------------------------------------------------------------------- |
| [NEW] `worker/tasks/vision_tasks.py` | Celery task `@task(queue='gpu_queue')` that runs the vision pipeline. |

---

### Application Layer (`backend/src/application/`)

| File                               | Purpose                                                            |
| :--------------------------------- | :----------------------------------------------------------------- |
| [NEW] `use_cases/process_video.py` | Use Case that triggers the async vision task and returns `job_id`. |

---

## Constraints Checklist (from infrastructure_spec.md)

| Constraint             | How We Enforce It                                                            |
| :--------------------- | :--------------------------------------------------------------------------- |
| **TDD**                | Tests created _before_ implementation.                                       |
| **Hexagonal Purity**   | `domain/` imports only `dataclasses`. YOLO/OpenCV stay in `infrastructure/`. |
| **GPU Queue Routing**  | Vision tasks use `@celery.task(queue='gpu_queue')`.                          |
| **JSON Error Logging** | Errors logged with `trace_id` using `structlog`.                             |

---

## Verification Plan

### TDD Commands

```bash
# 1. Run Domain Unit Tests
docker-compose exec api pytest tests/domain/test_trajectory.py -v

# 2. Run Vision Integration Tests (requires GPU worker)
docker-compose exec worker-gpu pytest tests/infrastructure/test_yolo_detector.py -v
```

### Manual Verification

1.  Upload a short video clip via `POST /api/v1/videos/process`.
2.  Verify `job_id` is returned immediately.
3.  Check Flower ([http://localhost:5555](http://localhost:5555)) for task in `gpu_queue`.
4.  After completion, verify Parquet file exists in MinIO bucket `trajectories/`.
