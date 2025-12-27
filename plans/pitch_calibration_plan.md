# Implementation Plan: Pitch Calibration Feature

## Goal

Implement the **Pitch Calibration** module as defined in [pitch_calibration_spec.md](../specs/pitch_calibration_spec.md), strictly adhering to the [infrastructure_spec.md](../specs/infrastructure_spec.md) constraints.

---

## User Review Required

> [!IMPORTANT] > **Domain Purity:** The Homography math logic will be in a pure Domain Service using only Python stdlib (no OpenCV). OpenCV stays in Infrastructure.

> [!WARNING] > **Async Processing:** Calibration runs in a background worker since line detection can be slow on large videos.

---

## Proposed Changes

### Domain Layer (`backend/src/domain/`)

| File                                       | Purpose                                                              |
| :----------------------------------------- | :------------------------------------------------------------------- |
| [NEW] `value_objects/homography_matrix.py` | Immutable 3x3 transformation matrix (List[List[float]]).             |
| [NEW] `value_objects/keypoint.py`          | `Keypoint` (pixel_x, pixel_y, pitch_x, pitch_y) for landmarks.       |
| [NEW] `services/calibration_service.py`    | Pure math: calculates $H$ matrix from 4+ keypoint pairs (no OpenCV). |
| [NEW] `ports/keypoint_detector.py`         | Abstract interface for detecting pitch landmarks.                    |

---

### Infrastructure Layer (`backend/src/infrastructure/`)

#### Computer Vision

| File                            | Purpose                                                            |
| :------------------------------ | :----------------------------------------------------------------- |
| [NEW] `cv/opencv_homography.py` | Adapter implementing homography using `cv2.findHomography()`.      |
| [NEW] `cv/line_detector.py`     | Adapter implementing `KeypointDetector` using edge/line detection. |

#### Worker

| File                                      | Purpose                            |
| :---------------------------------------- | :--------------------------------- |
| [NEW] `worker/tasks/calibration_tasks.py` | Celery task for async calibration. |

---

### Application Layer (`backend/src/application/`)

| File                                   | Purpose                                                            |
| :------------------------------------- | :----------------------------------------------------------------- |
| [NEW] `use_cases/start_calibration.py` | Orchestrator that triggers async calibration and returns `job_id`. |

---

## Constraints Checklist (from infrastructure_spec.md)

| Constraint           | How We Enforce It                                              |
| :------------------- | :------------------------------------------------------------- |
| **TDD**              | Tests created _before_ implementation.                         |
| **Hexagonal Purity** | `domain/` uses only stdlib math. OpenCV in `infrastructure/`.  |
| **Celery Routing**   | Calibration uses `@celery.task(queue='default')` (CPU task).   |
| **Edge Case**        | If < 4 keypoints found, flag as "Manual Calibration Required". |

---

## Verification Plan

### TDD Commands

```bash
# 1. Run Domain Unit Tests (Pure Math)
docker-compose exec api pytest tests/domain/test_calibration_service.py -v

# 2. Run Infrastructure Tests (OpenCV)
docker-compose exec api pytest tests/infrastructure/test_homography.py -v
```

### Manual Verification

1.  `POST /api/v1/calibration/start` with `{"video_id": "..."}`.
2.  Verify `job_id` is returned.
3.  Poll `/api/v1/jobs/{job_id}` until status is `COMPLETED` or `MANUAL_REQUIRED`.
4.  Verify the $H$ matrix is stored in the database.
