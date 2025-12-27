# ✨ Feature Specification: Dashboard Infrastructure

> **Context:** This is the umbrella spec for the [UI Dashboard](./ui_dashboard_spec.md) feature. It defines the foundational architecture that supports all UI components.

## 1. 🚀 Overview & Motivation

- **Feature Name:** Dashboard Infrastructure & Foundation
- **Goal:** Establish a robust, scalable, and maintainable Next.js architecture for the analyst dashboard.
- **Problem Solved (The "Why"):** Provides the technical foundation (routing, state management, API integration, theming) that all UI components depend on.
- **Scope:**
  - **In Scope:** Next.js setup, global state management, API client, routing structure, design system integration.
  - **Out of Scope:** Component-specific features (see individual specs).

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Frontend Developer**, I want **a decoupled API**, so that **I can build the UI without fighting Python's synchronous nature.**

| Criteria ID | Acceptance Criteria                                                                                             | Status |
| :---------- | :-------------------------------------------------------------------------------------------------------------- | :----- |
| US1.1       | The UI SHALL fetch data asynchronously from the Python API (`GET /matches/{id}/tracking`) using TanStack Query. | [ ]    |
| US1.2       | The UI SHALL NOT block interactions while fetching data (non-blocking).                                         | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture & Dependencies**

- **Framework:** Next.js 14+ (App Router, TypeScript)
- **State Management:** `zustand` (global state)
- **Data Fetching:** `@tanstack/react-query`
- **Styling:** TailwindCSS + `shadcn/ui`
- **API Client:** `axios` or `fetch`

### **3.2 Project Structure**

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   └── matches/
│       └── [id]/
│           ├── page.tsx    # Match detail page
│           └── components/ # Match-specific components
├── components/
│   ├── ui/                 # Shadcn components
│   ├── video-player/       # VideoPlayer component
│   ├── pitch-view/         # TacticalBoard component
│   ├── metrics/            # MetricsCharts component
│   ├── chat/               # ChatInterface component
│   └── reporting/          # ReportGenerator component
├── lib/
│   ├── api.ts              # API client
│   ├── store.ts            # Zustand store
│   └── utils.ts            # Utilities
└── styles/
    └── globals.css         # Global styles
```

### **3.3 Global State (Zustand)**

```typescript
interface MatchStore {
  matchId: string | null;
  currentFrame: number;
  currentTimestamp: number;
  setCurrentFrame: (frame: number) => void;
  setCurrentTimestamp: (timestamp: number) => void;
}
```

### **3.4 API Client**

- Base URL: `http://localhost:8000/api/v1`
- Endpoints:
  - `GET /matches` - List matches
  - `GET /matches/{id}` - Match details
  - `GET /matches/{id}/tracking` - Tracking data
  - `GET /matches/{id}/metrics` - Metrics
  - `POST /chat/analyze` - Start analysis
  - `GET /chat/jobs/{job_id}` - Job status

### **3.5 Implementation Steps**

1. **Scaffold:** `npx create-next-app@latest` with TypeScript/Tailwind
2. **Install Dependencies:**
   ```bash
   npm install zustand @tanstack/react-query axios shadcn-ui
   ```
3. **Setup Shadcn:**
   ```bash
   npx shadcn-ui@latest init
   ```
4. **Create Store:** Implement Zustand store
5. **API Client:** Create axios instance with interceptors
6. **Routing:** Setup App Router structure

---

## 4. 🔒 Constraints & Edge Cases

- **Constraints:**
  - **Strict TypeScript:** No `any` types allowed
  - **Theme:** Dark mode by default
  - **Performance:** First Contentful Paint < 2s
- **Edge Cases:**
  - **API Down:** Show connection error banner
  - **Slow Network:** Show loading skeletons

---

## 5. 🧪 Testing & Validation Plan

- **Tools:**
  - `Vitest`: Unit tests
  - `Playwright`: E2E tests
  - `Lighthouse`: Performance audits
- **Test Scenarios:**
  - **Scenario 1:** Navigate to `/matches/123` → Page loads with data
  - **Scenario 2:** API returns 500 → Error toast appears

---

## 6. 🔗 Related Specifications

- [Video Player](./video_player_spec.md)
- [Pitch Visualization](./pitch_visualization_spec.md)
- [Metrics Dashboard](./metrics_dashboard_spec.md)
- [Chat Interface](./chat_interface_spec.md)
- [Reporting](./reporting_spec.md)
