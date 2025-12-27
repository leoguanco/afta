# ✨ Feature Specification: UI Dashboard & Reporting

## 1. 🚀 Overview & Motivation

- **Feature Name:** Analyst Dashboard (Next.js/React)
- **Goal:** Provide a high-performance, interactive, and aesthetically premium web interface for match analysis.
- **Problem Solved (The "Why"):** Streamlit and Python-based UIs are limiting for complex interactions (video scrubbing + canvas drawing + simultaneous chart updates). Moving to a React-based frontend allows for a decoupled, production-grade architecture that consumes the pure Python Domain API.
- **Scope:**
  - **In Scope:** Next.js (App Router), Shadcn/UI Component Library, TailwindCSS, React Player, Recharts/Nivo, Axios/TanStack Query.
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
| US2.1       | The Video Player SHALL support an overlay canvas (HTMl5 Canvas or SVG) for drawing arrows/shapes.              | [ ]    |
| US2.2       | The drawing state SHALL be synchronized with the video timestamp (Drawings appear only at relevant keyframes). | [ ]    |

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
  - `recharts`: For tactical metrics charts.
  - `react-player`: For video control.
  - `zustand`: For global state management (Video Timestamp <-> Map Sync).
- **Data Model Changes:**
  - API must return JSON payloads optimized for frontend consumption (e.g., GeoJSON for pitch data).

### **3.2 Implementation Steps (High-Level)**

1.  **Scaffold:** `npx create-next-app@latest` with TypeScript/Tailwind.
2.  **State Mgmt:** Setup Zustand store to hold `currentFrame` and `matchData`.
3.  **Components:** Build `VideoPlayer` and `TacticalBoard` (D3.js or SVG based).
4.  **Integration:** Connect to FastAPI endpoints.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - **Strict Typing:** TypeScript must be used; `any` types are forbidden.
  - **Design System:** Must use Shadcn/UI for a consistent "Premium" look.
- **Assumptions:**
  - Node.js (v18+) is installed on the dev environment.
- **Edge Cases & Error Handling:**
  - **API Down:** UI must show a "Connection Lost" toast and retry button.
  - **Large Payloads:** If tracking data is too big (50MB+), UI should request chunked data or use a binary format (Protobuf/Arrow) - _Start with JSON for MVP_.

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** Component Testing + E2E.
- **Tools:** `Vitest` (Unit), `Playwright` (E2E).
- **Key Test Scenarios:**
  - **Scenario 1:** Click on a "Goal" event in the timeline -> Video jumps to that timestamp.
  - **Scenario 2:** Resize browser window -> Pitch Map rescales correctly without distortion.

---

## 6. 🔗 References and Related Documentation

- [Next.js Documentation](https://nextjs.org/docs)
- [Shadcn/UI](https://ui.shadcn.com/)
