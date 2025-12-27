# ✨ Feature Specification: Video Player Component

> **Context:** This spec is part of the [UI Dashboard](./ui_dashboard_spec.md) feature. For infrastructure setup, see [dashboard_infrastructure_spec.md](./dashboard_infrastructure_spec.md).

## 1. 🚀 Overview & Motivation

- **Feature Name:** Interactive Video Player with Drawing Overlay
- **Goal:** Provide a professional video playback interface with synchronized tactical annotation capabilities.
- **Problem Solved (The "Why"):** Analysts need to annotate key moments (passes, runs, space) directly on video frames for tactical review sessions.
- **Scope:**
  - **In Scope:** Video playback controls, canvas overlay for drawing, timestamp synchronization, frame-by-frame navigation.
  - **Out of Scope:** Video editing/cutting, multi-camera angles.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Tactical Analyst**, I want to **draw on the video**, so that **I can highlight space and movements.**

| Criteria ID | Acceptance Criteria                                                                                            | Status |
| :---------- | :------------------------------------------------------------------------------------------------------------- | :----- |
| US1.1       | The Video Player SHALL support an overlay canvas (HTML5 Canvas or SVG) for drawing arrows/shapes.              | [ ]    |
| US1.2       | The drawing state SHALL be synchronized with the video timestamp (Drawings appear only at relevant keyframes). | [ ]    |
| US1.3       | Drawings SHALL persist when scrubbing back to the same timestamp.                                              | [ ]    |

### **User Story 2:** As an **Analyst**, I want to **control playback**, so that **I can review specific moments.**

| Criteria ID | Acceptance Criteria                                                              | Status |
| :---------- | :------------------------------------------------------------------------------- | :----- |
| US2.1       | The player SHALL support play/pause, seek, and playback speed control (0.5x-2x). | [ ]    |
| US2.2       | The player SHALL support frame-by-frame navigation (arrow keys).                 | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture**

- **Component:** `VideoPlayer` (React)
- **Dependencies:**
  - `react-player`: Video playback
  - HTML5 Canvas API or `konva.js`: Drawing overlay
  - `zustand`: Global state for `currentTimestamp`

### **3.2 Implementation Steps**

1. **Video Component:** Integrate `react-player` with custom controls.
2. **Canvas Overlay:** Layer canvas on top of video element.
3. **Drawing Tools:** Implement line/arrow/circle drawing with mouse events.
4. **State Sync:** Update global `currentTimestamp` on video timeupdate.

---

## 4. 🔒 Constraints & Edge Cases

- **Constraints:**
  - Video formats: MP4 (H.264) only for MVP.
  - Drawing tools: Line, Arrow, Circle, Freehand.
- **Edge Cases:**
  - **Video Load Failure:** Display error message with retry button.
  - **Large Video Files:** Show loading progress bar.

---

## 5. 🧪 Testing & Validation Plan

- **Test Scenarios:**
  - **Scenario 1:** Draw an arrow at 00:30 → Scrub to 01:00 → Scrub back to 00:30 → Arrow reappears.
  - **Scenario 2:** Press spacebar → Video pauses/plays.
