# 👁️ Feature Spec: Vision Engine

## 1. 🚀 Overview

The **Vision Engine** is the core data acquisition module. It transforms raw video footage into structured, spatio-temporal data (2D coordinates) for every player and the ball.

**Goal:** Achieve >90% detection accuracy and consistent ID tracking to minimize manual correction.

---

## 2. 🏗️ Technical Architecture

### 2.1 Pipeline Steps

1.  **Frame Extraction:** Read video specifically at 25/30 FPS.
2.  **Object Detection (YOLOv8):** Identify bounding boxes for classes: `0: ball`, `1: referee`, `2: player`.
3.  **Team Classification:** Use color histograms (K-Means) inside bounding boxes to assign `Team A`, `Team B`, or `Goalkeeper`.
4.  **Object Tracking (ByteTrack):** Associate detections across frames to assign unique `Target IDs`.
5.  **Camera Calibration (Homography):**
    - Detect pitch keypoints (intersections of lines).
    - Compute Homography Matrix `H`.
    - Transform `(u, v)` pixel coordinates to `(x, y)` pitch meters.
6.  **Smoothing:** Apply Kalman Filter or Savitzky-Golay filter to reduce jitter.

---

## 3. 📝 Data Schemas

### 3.1 Raw Tracking Output (Parquet/CSV)

File: `match_{id}_tracking.parquet`

| Column         | Type   | Description                       |
| :------------- | :----- | :-------------------------------- |
| `frame_id`     | int    | Video frame number                |
| `timestamp`    | float  | Seconds from kickoff              |
| `object_id`    | int    | Unique tracking ID (e.g., 104)    |
| `object_class` | string | 'player', 'ball', 'referee'       |
| `team_id`      | int    | 0 (Home), 1 (Away), -1 (Ref/Ball) |
| `x`            | float  | Pitch coordinate length (0-105m)  |
| `y`            | float  | Pitch coordinate width (0-68m)    |
| `v_x`          | float  | Velocity X (m/s)                  |
| `v_y`          | float  | Velocity Y (m/s)                  |

---

## 4. ⚙️ Configuration & Constraints

- **Input Resolution:** Minimum 1080p (1920x1080) for small object (ball) detection.
- **Hardware:**
  - NVIDIA GPU (min 6GB VRAM) recommended for YOLOv8 (Medium/Large models).
  - CPU-only mode supported but slow (< 5 FPS).
- **Homography Fallback:**
  - If automatic keypoint detection fails (e.g., zoom-in), prompt user to select 4 points manually on the first frame.

---

## 5. ✅ Acceptance Criteria

| ID        | Criteria                                                          | Test Method               |
| :-------- | :---------------------------------------------------------------- | :------------------------ |
| **VE-01** | Support MP4, AVI, and MOV formats.                                | Manual Upload             |
| **VE-02** | Detect Ball with >80% recall.                                     | Benchmark vs Ground Truth |
| **VE-03** | Auto-detect at least 4 pitch points in wide-angle logical frames. | Unit Test on Sample Set   |
| **VE-04** | Output coordinates aligned to standard 105x68m pitch.             | Visual Inspection (Plot)  |
