# 📋 Implementation Plan: Highlight Mode

> **Spec:** [12_highlight_mode_spec.md](12_highlight_mode_spec.md) > **Dependencies:** Feature 10 (Event Recognition), Feature 11 (Match Metadata)

---

## Phase 1: Scene Detection

### 1.1 Scene Detector

#### [NEW] `src/domain/services/scene_detector.py`

- Implement `SceneDetector` class
- Use frame differencing (OpenCV) to detect cuts
- Threshold: `diff > 30%` = scene change
- Output: `List[Scene]` with `start_frame`, `end_frame`

---

## Phase 2: API Updates

### 2.1 Request Model

#### [MODIFY] `src/infrastructure/api/endpoints/video.py`

- Update `VideoProcessRequest` to include:
  - `mode: Literal["full_match", "highlights"] = "full_match"`

---

## Phase 3: Vision Task Updates

### 3.1 Highlight Processing

#### [MODIFY] `src/infrastructure/worker/tasks/vision_tasks.py`

- If `mode == "highlights"`:
  1. Run `SceneDetector`
  2. For each scene:
     - Reset tracker
     - Process scene frames
     - Run Event Detection
  3. Skip metrics chaining (no total distance)
  4. Index scene labels to RAG

---

## Phase 4: Scene Classification (Phase 2 of Feature)

### 4.1 Action Classifier

#### [NEW] `src/infrastructure/ml/action_classifier.py`

- Implement `ActionClassifier` (future: SlowFast model)
- MVP: Heuristic (ball near goal area = "Shot/Goal")

---

## Verification Plan

1. **Unit Tests:**

   - `test_scene_detector.py`: Assert 3 scenes detected in test video with 3 cuts

2. **Integration Test:**
   - Process 2-minute highlight reel
   - Verify output contains multiple scenes
   - Verify metrics are NOT calculated (no distance/possession)
