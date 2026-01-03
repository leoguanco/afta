# ✨ Feature Specification: Highlight Mode

## 1. 🚀 Overview & Motivation

- **Feature Name:** Highlight Mode
- **Goal:** Process highlight videos (compilations of key moments) differently from full-match footage.
- **Problem Solved:** Highlight videos have cuts, jumps, and discontinuous tracking. Standard metrics (distance, possession %) are meaningless. We need scene-aware processing.
- **Scope:**
  - **Scene Detection:** Identify cut points in the video.
  - **Per-Clip Analysis:** Analyze each segment independently.
  - **Action Classification:** Label segments (Goal, Save, Foul).

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **User**, I want to **upload highlight videos** without broken metrics.

| Criteria ID | Acceptance Criteria                                              | Status |
| :---------- | :--------------------------------------------------------------- | :----- |
| US1.1       | API SHALL accept `mode: "highlights"` parameter.                 | [ ]    |
| US1.2       | In highlight mode, system SHALL skip total distance calculation. | [ ]    |
| US1.3       | In highlight mode, system SHALL skip possession % calculation.   | [ ]    |

### **User Story 2:** As a **User**, I want the system to **detect scene changes**.

| Criteria ID | Acceptance Criteria                                              | Status |
| :---------- | :--------------------------------------------------------------- | :----- |
| US2.1       | System SHALL detect scene cuts using frame difference threshold. | [ ]    |
| US2.2       | System SHALL reset tracker IDs after each scene cut.             | [ ]    |
| US2.3       | System SHALL output a list of `scenes` with start/end frames.    | [ ]    |

### **User Story 3:** As a **User**, I want each **clip labeled by action type**.

| Criteria ID | Acceptance Criteria                                                    | Status |
| :---------- | :--------------------------------------------------------------------- | :----- |
| US3.1       | System SHALL attempt to classify each scene (Goal, Shot, Foul, Other). | [ ]    |
| US3.2       | Classification MAY use heuristics (ball near goal area) or AI model.   | [ ]    |
| US3.3       | Results SHALL be indexed to RAG for AI analysis.                       | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Scene Detection**

```python
class SceneDetector:
    def detect_scenes(self, video_path: str) -> List[Scene]:
        # Use OpenCV frame differencing or PySceneDetect
        pass

@dataclass
class Scene:
    start_frame: int
    end_frame: int
    label: Optional[str] = None
```

### **3.2 Per-Scene Processing**

1. For each scene, reset ByteTracker.
2. Run tracking on scene frames only.
3. Run Event Detection on scene.
4. Classify scene action.

### **3.3 API Changes**

```python
class VideoProcessRequest(BaseModel):
    video_path: str
    output_path: str
    mode: Literal["full_match", "highlights"] = "full_match"  # NEW
```

---

## 4. 🧪 Testing & Validation Plan

- **Unit Tests:**
  - Assert scene detection on a test video with 3 known cuts.
- **Integration Tests:**
  - Process a 2-minute highlight reel.
  - Verify output contains multiple scenes with labels.

---

## 5. 🔗 Dependencies

- Requires: **Event Recognition Engine** (Feature 10) for action classification.
- Requires: **Match Metadata** (Feature 11) for scene tagging context.
