# 📋 Implementation Plan: Match Metadata & Sync

> **Spec:** [11_match_metadata_spec.md](11_match_metadata_spec.md)

---

## Phase 1: API Updates

### 1.1 Request Model

#### [MODIFY] `src/infrastructure/api/endpoints/video.py`

- Add `MatchMetadata` Pydantic model
- Update `VideoProcessRequest` to include:
  - `metadata: Optional[MatchMetadata]`
  - `sync_offset_seconds: float = 0.0`

---

## Phase 2: VideoProcessor Updates

### 2.1 Use Case Changes

#### [MODIFY] `src/application/use_cases/video_processor.py`

- Update `execute()` signature to accept `metadata` and `sync_offset`
- Logic:
  1. Check if Match exists by `match_id`
  2. If exists: Attach video, don't overwrite metadata
  3. If not: Create Match from `metadata` or use placeholders
- Store `sync_offset` in Match entity for later use

---

## Phase 3: Sync Utility

### 3.1 Frame-to-Timestamp Conversion

#### [NEW] `src/domain/services/time_sync.py`

- Implement `frame_to_timestamp(frame_id, fps, offset) -> float`
- Implement `timestamp_to_frame(timestamp, fps, offset) -> int`

#### [MODIFY] `src/application/use_cases/metrics_calculator.py`

- Use sync functions when correlating video frames with event timestamps

---

## Verification Plan

1. **Unit Tests:**

   - `test_time_sync.py`: Assert frame 150 @ 25fps + 300s offset = 306s

2. **Integration Test:**
   - Ingest StatsBomb match 3788741
   - Upload video named `3788741.mp4`
   - Verify Match has merged data (events + tracking)
