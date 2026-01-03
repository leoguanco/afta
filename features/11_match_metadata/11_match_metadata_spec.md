# ✨ Feature Specification: Match Metadata & Video-Data Sync

## 1. 🚀 Overview & Motivation

- **Feature Name:** Match Metadata & Video-Data Sync
- **Goal:** Enable rich match metadata (teams, lineups, date) for video uploads and synchronize video frames with external event data (StatsBomb).
- **Problem Solved:** Currently, video uploads create placeholder matches ("Home vs Away"). Users need to provide team names, link videos to existing match data, and sync timestamps.
- **Scope:**
  - **Metadata Input:** Accept team names, date, competition via API.
  - **Auto-Link:** If `match_id` already exists (from ingestion), attach video tracking to it.
  - **Time Sync:** Align video frame numbers with match timestamps.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **User**, I want to **provide team names** when uploading a video.

| Criteria ID | Acceptance Criteria                                                             | Status |
| :---------- | :------------------------------------------------------------------------------ | :----- |
| US1.1       | `/api/v1/process-video` SHALL accept optional `metadata` object.                | [ ]    |
| US1.2       | `metadata` SHALL support `home_team`, `away_team`, `date`, `competition`.       | [ ]    |
| US1.3       | System SHALL use provided metadata instead of placeholders when creating Match. | [ ]    |

### **User Story 2:** As a **User**, I want to **link video to existing StatsBomb data**.

| Criteria ID | Acceptance Criteria                                                             | Status |
| :---------- | :------------------------------------------------------------------------------ | :----- |
| US2.1       | If a Match with `match_id` already exists, video processing SHALL attach to it. | [ ]    |
| US2.2       | System SHALL NOT overwrite existing team/lineup data.                           | [ ]    |
| US2.3       | System SHALL merge tracking data with existing event data.                      | [ ]    |

### **User Story 3:** As a **User**, I want to **sync video time with match time**.

| Criteria ID | Acceptance Criteria                                                    | Status |
| :---------- | :--------------------------------------------------------------------- | :----- |
| US3.1       | API SHALL accept `sync_offset_seconds` parameter.                      | [ ]    |
| US3.2       | System SHALL convert Frame N to `timestamp = (N / fps) + sync_offset`. | [ ]    |
| US3.3       | Events from StatsBomb SHALL be alignable with video frames.            | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 API Changes**

```python
# video.py
class VideoProcessRequest(BaseModel):
    video_path: str
    output_path: str
    metadata: Optional[MatchMetadata] = None  # NEW
    sync_offset_seconds: float = 0.0  # NEW

class MatchMetadata(BaseModel):
    home_team: str
    away_team: str
    date: Optional[str] = None
    competition: Optional[str] = None
```

### **3.2 VideoProcessor Updates**

1. Check if Match exists by `match_id`.
2. If exists: Use existing data, attach video.
3. If not: Create Match from `metadata` or use placeholders.

### **3.3 Sync Logic**

```python
def frame_to_timestamp(frame_id: int, fps: float, offset: float) -> float:
    return (frame_id / fps) + offset
```

---

## 4. 🧪 Testing & Validation Plan

- **Unit Tests:**
  - Assert metadata is stored correctly in Match entity.
  - Assert existing matches are not overwritten.
- **Integration Tests:**
  - Ingest StatsBomb match, then upload video with same ID.
  - Verify events and tracking data are linked.
