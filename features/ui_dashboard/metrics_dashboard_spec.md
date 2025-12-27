# ✨ Feature Specification: Metrics Dashboard Component

> **Context:** This spec is part of the [UI Dashboard](./ui_dashboard_spec.md) feature. For infrastructure setup, see [dashboard_infrastructure_spec.md](./dashboard_infrastructure_spec.md).

## 1. 🚀 Overview & Motivation

- **Feature Name:** Tactical Metrics Dashboard
- **Goal:** Display time-series charts and statistical summaries of tactical metrics.
- **Problem Solved (The "Why"):** Coaches need to identify patterns over the course of a match (e.g., when pressing intensity drops).
- **Scope:**
  - **In Scope:** Time-series charts (PPDA, Pitch Control, Speed), filtering by period, player comparison.
  - **Out of Scope:** Predictive analytics, real-time live match tracking.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Coach**, I want to **view metrics over time**, so that **I can identify tactical patterns.**

| Criteria ID | Acceptance Criteria                                                     | Status |
| :---------- | :---------------------------------------------------------------------- | :----- |
| US1.1       | The UI SHALL display time-series charts for PPDA, Pitch Control, Speed. | [ ]    |
| US1.2       | The UI SHALL allow filtering by match period (First Half/Second Half).  | [ ]    |

### **User Story 2:** As an **Analyst**, I want to **compare players**, so that **I can benchmark performance.**

| Criteria ID | Acceptance Criteria                                                             | Status |
| :---------- | :------------------------------------------------------------------------------ | :----- |
| US2.1       | The UI SHALL display a bar chart comparing total distance for selected players. | [ ]    |
| US2.2       | The UI SHALL support multi-select for up to 5 players.                          | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture**

- **Component:** `MetricsCharts` (React)
- **Dependencies:**
  - `recharts` or `nivo`: Chart library
  - `@tanstack/react-query`: Data fetching
  - `shadcn/ui`: Select components

### **3.2 Implementation Steps**

1. **Chart Components:** Build `PPDAChart`, `PitchControlChart`, `SpeedChart`.
2. **Data Fetching:** Query `/api/v1/matches/{id}/metrics` endpoint.
3. **Filtering Logic:** Implement period and player filters.
4. **Responsive Design:** Ensure charts scale on mobile.

---

## 4. 🔒 Constraints & Edge Cases

- **Constraints:**
  - Charts must use consistent color scheme (team colors).
  - Data refresh: Maximum 1 request per 5 seconds.
- **Edge Cases:**
  - **No Data:** Display "No metrics available for this match."

---

## 5. 🧪 Testing & Validation Plan

- **Test Scenarios:**
  - **Scenario 1:** Select "First Half" filter → Chart updates to show only 0-45 min data.
  - **Scenario 2:** Select 3 players → Bar chart displays 3 bars.
