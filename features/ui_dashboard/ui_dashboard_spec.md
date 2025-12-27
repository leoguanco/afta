# ✨ Feature Specification: UI Dashboard & Reporting

> **Context:** This spec is part of the [Football Intelligence Engine](../../feature_specs.md) project. For infrastructure setup (Next.js, Docker, API integration), see [../infrastructure/infrastructure_spec.md](../infrastructure/infrastructure_spec.md).

## 1. 🚀 Overview & Motivation

- **Feature Name:** Analyst Dashboard (Next.js/React)
- **Goal:** Provide a high-performance, interactive, and aesthetically premium web interface for match analysis with real-time video playback, pitch visualization, and AI-powered chat.
- **Problem Solved (The "Why"):** Python-based UIs (Streamlit) are limiting for complex interactions (video scrubbing + canvas drawing + simultaneous chart updates). Moving to a React-based frontend allows for a decoupled, production-grade architecture that consumes the pure Python Domain API.
- **Scope:**
  - **In Scope:** Next.js (App Router), Shadcn/UI Component Library, TailwindCSS, React Player, Recharts/Nivo, Axios/TanStack Query, Interactive Pitch View, AI Chat Interface, PDF Report Generation.
  - **Out of Scope:** Mobile Native features (PWA is sufficient for now).

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Frontend Developer**, I want **a decoupled API**, so that **I can build the UI without fighting Python's synchronous nature.**

| Criteria ID | Acceptance Criteria                                                                                             | Status |
| :---------- | :-------------------------------------------------------------------------------------------------------------- | :----- |
| US1.1       | The UI SHALL fetch data asynchronously from the Python API (`GET /matches/{id}/tracking`) using TanStack Query. | [ ]    |
| US1.2       | The UI SHALL NOT block the video playback while fetching new metrics (Non-blocking).                            | [ ]    |

### **User Story 2:** As a **Tactical Analyst**, I want to **draw on the video**, so that **I can highlight space.**

| Criteria ID | Acceptance Criteria                                                                                            | Status |
| :---------- | :------------------------------------------------------------------------------------------------------------- | :----- |
| US2.1       | The Video Player SHALL support an overlay canvas (HTML5 Canvas or SVG) for drawing arrows/shapes.              | [ ]    |
| US2.2       | The drawing state SHALL be synchronized with the video timestamp (Drawings appear only at relevant keyframes). | [ ]    |

### **User Story 3:** As a **Coach**, I want to **view metrics over time**, so that **I can identify tactical patterns.**

| Criteria ID | Acceptance Criteria                                                     | Status |
| :---------- | :---------------------------------------------------------------------- | :----- |
| US3.1       | The UI SHALL display time-series charts for PPDA, Pitch Control, Speed. | [ ]    |
| US3.2       | The UI SHALL allow filtering by match period (First Half/Second Half).  | [ ]    |

### **User Story 4:** As an **Analyst**, I want to **chat with AI about the match**, so that **I can get insights quickly.**

| Criteria ID | Acceptance Criteria                                                      | Status |
| :---------- | :----------------------------------------------------------------------- | :----- |
| US4.1       | The Chat interface SHALL connect to the `/api/v1/chat/analyze` endpoint. | [ ]    |
| US4.2       | The Chat SHALL poll for job status and display results when ready.       | [ ]    |

### **User Story 5:** As a **Coach**, I want to **download a PDF report**, so that **I can share insights with staff.**

| Criteria ID | Acceptance Criteria                                                             | Status |
| :---------- | :------------------------------------------------------------------------------ | :----- |
| US5.1       | The UI SHALL generate a PDF with match summary, graphs, and AI recommendations. | [ ]    |
| US5.2       | The PDF SHALL contain at least 2 graphs and 1 text summary.                     | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture and Dependencies**

- **Architecture Pattern:** **Client-Server (Decoupled)**
  - **Frontend:** Next.js 14+ (TypeScript).
  - **Backend:** FastAPI (Python) - _See Infrastructure Spec_.
  - **Communication:** REST API + WebSockets (for real-time Agent chat).
- **New Dependencies (Frontend):**
  - `next`: React Framework.
  - `tailwindcss` + `shadcn/ui`: Styling and accessible components.
  - `recharts` or `nivo`: For tactical metrics charts.
  - `react-player`: For video control.
  - `zustand`: For global state management (Video Timestamp <-> Map Sync).
  - `@tanstack/react-query`: For API data fetching and caching.
  - `jspdf` or `react-pdf`: For PDF report generation.
- **Data Model Changes:**
  - API must return JSON payloads optimized for frontend consumption (e.g., GeoJSON for pitch data).

### **3.2 UI Layout**

1.  **Sidebar (Controls):**

    - Match Selection Dropdown.
    - Analysis Mode (Full Match / Clip / Set-piece).
    - Team Configuration (Colors, Names).
    - "Generate Report" Button.

2.  **Main View (Tabs):**
    - **Tab 1: Video Player:** Playback with overlaid tracking bounding boxes and drawing canvas.
    - **Tab 2: Pitch View:** 2D Top-down animation of player dots + Voronoi diagrams / Pitch Control heatmaps.
    - **Tab 3: Metrics:** Time-series charts (e.g., PPDA, Pitch Control over 90 mins).
    - **Tab 4: AI Chat:** Chatbot interface to query the match data.

### **3.3 Implementation Steps (High-Level)**

1.  **Scaffold:** `npx create-next-app@latest` with TypeScript/Tailwind.
2.  **State Mgmt:** Setup Zustand store to hold `currentFrame` and `matchData`.
3.  **Components:**
    - Build `VideoPlayer` (React Player with overlay canvas).
    - Build `TacticalBoard` (D3.js or SVG based).
    - Build `MetricsCharts` (Recharts).
    - Build `ChatInterface` (with polling logic).
4.  **Integration:** Connect to FastAPI endpoints.
5.  **Reporting:** Implement PDF generation using `jspdf`.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - **Strict Typing:** TypeScript must be used; `any` types are forbidden.
  - **Design System:** Must use Shadcn/UI for a consistent "Premium" look.
  - **Performance:** Render top-down pitch view at >15 FPS.
  - **Theme:** Dark mode by default (better for video analysis).
- **Assumptions:**
  - Node.js (v18+) is installed on the dev environment.
- **Edge Cases & Error Handling:**
  - **API Down:** UI must show a "Connection Lost" toast and retry button.
  - **Large Payloads:** If tracking data is too big (50MB+), UI should request chunked data or use a binary format (Protobuf/Arrow) - _Start with JSON for MVP_.
  - **Chat Timeout:** If AI analysis takes >60s, show "Still processing..." message.

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** Component Testing + E2E.
- **Tools:** `Vitest` (Unit), `Playwright` (E2E).
- **Key Test Scenarios:**
  - **Scenario 1:** Click on a "Goal" event in the timeline -> Video jumps to that timestamp.
  - **Scenario 2:** Resize browser window -> Pitch Map rescales correctly without distortion.
  - **Scenario 3:** Submit chat query -> Poll status -> Display result when completed.
  - **Scenario 4:** Generate PDF -> Verify it contains graphs and summary.

---

## 6. 🔗 References and Related Documentation

- [Next.js Documentation](https://nextjs.org/docs)
- [Shadcn/UI](https://ui.shadcn.com/)
- [TanStack Query](https://tanstack.com/query/latest)
- [Recharts](https://recharts.org/)
