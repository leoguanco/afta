# ✨ Feature Specification: Pitch Visualization Component

> **Context:** This spec is part of the [UI Dashboard](./ui_dashboard_spec.md) feature. For infrastructure setup, see [dashboard_infrastructure_spec.md](./dashboard_infrastructure_spec.md).

## 1. 🚀 Overview & Motivation

- **Feature Name:** Interactive 2D Pitch Visualization
- **Goal:** Provide a top-down tactical view of player positions, movements, and spatial control.
- **Problem Solved (The "Why"):** Coaches need to see spatial relationships and team shape that are difficult to perceive from video alone.
- **Scope:**
  - **In Scope:** Player tracking dots, heatmaps (Pitch Control), Voronoi diagrams, frame-by-frame animation, synchronized with video.
  - **Out of Scope:** 3D visualization, VR support.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Coach**, I want to **see player positions**, so that **I can analyze team shape.**

| Criteria ID | Acceptance Criteria                                                              | Status |
| :---------- | :------------------------------------------------------------------------------- | :----- |
| US1.1       | The pitch view SHALL display all 22 players as colored dots with jersey numbers. | [ ]    |
| US1.2       | Player positions SHALL update in sync with video timestamp (±100ms tolerance).   | [ ]    |

### **User Story 2:** As a **Tactical Analyst**, I want to **visualize Pitch Control**, so that **I can identify space domination.**

| Criteria ID | Acceptance Criteria                                                                 | Status |
| :---------- | :---------------------------------------------------------------------------------- | :----- |
| US2.1       | The pitch SHALL display a Pitch Control heatmap overlay (fetched from backend API). | [ ]    |
| US2.2       | The heatmap SHALL use a diverging color scale (Team A = Blue, Team B = Red).        | [ ]    |

### **User Story 3:** As an **Analyst**, I want to **toggle visualization layers**, so that **I can focus on specific metrics.**

| Criteria ID | Acceptance Criteria                                              | Status |
| :---------- | :--------------------------------------------------------------- | :----- |
| US3.1       | The UI SHALL provide toggles for: Player Dots, Heatmap, Voronoi. | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture**

- **Component:** `TacticalBoard` (React + SVG or D3.js)
- **Dependencies:**
  - `d3.js` or `visx`: SVG rendering
  - `@tanstack/react-query`: Data fetching
  - `zustand`: Global state for `currentFrame`

### **3.2 Implementation Steps**

1. **Pitch SVG:** Render standard pitch markings (105m x 68m).
2. **Player Dots:** Map tracking data to SVG circles.
3. **Heatmap Layer:** Render Pitch Control grid as colored rectangles.
4. **Sync Logic:** Subscribe to `currentFrame` from Zustand store.

---

## 4. 🔒 Constraints & Edge Cases

- **Constraints:**
  - **Performance:** Must render at >15 FPS.
  - **Responsive:** Pitch must scale without distortion on resize.
- **Edge Cases:**
  - **Missing Tracking Data:** Display "No tracking data for this frame."

---

## 5. 🧪 Testing & Validation Plan

- **Test Scenarios:**
  - **Scenario 1:** Resize browser window → Pitch rescales proportionally.
  - **Scenario 2:** Toggle heatmap OFF → Player dots remain visible.
