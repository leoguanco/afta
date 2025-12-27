# ✨ Feature Specification: UI Dashboard & Reporting

> **Context:** This is the main specification document for the UI Dashboard feature. For detailed component specifications, see the enumerated spec folders listed below.

## 📑 Component Specifications (Implementation Order)

The UI Dashboard is divided into 6 enumerated components. Follow the numbering for implementation order:

### 01. [Dashboard Infrastructure](./01_dashboard_infrastructure/01_dashboard_infrastructure_spec.md)

**Foundation** - Next.js setup, routing, state management (Zustand), API client, design system (Shadcn/UI)

### 02. [Video Player](./02_video_player/02_video_player_spec.md)

**Core Component** - Video playback with React Player, drawing overlay canvas, timestamp synchronization

### 03. [Pitch Visualization](./03_pitch_visualization/03_pitch_visualization_spec.md)

**Visual Analysis** - Interactive 2D pitch view, player tracking dots, heatmaps, Voronoi diagrams

### 04. [Metrics Dashboard](./04_metrics_dashboard/04_metrics_dashboard_spec.md)

**Statistics** - Time-series charts (Recharts), PPDA/Speed/Distance graphs, filtering by period/player

### 05. [Chat Interface](./05_chat_interface/05_chat_interface_spec.md)

**AI Integration** - AI-powered match analysis chat, job polling, message history

### 06. [Reporting](./06_reporting/06_reporting_spec.md)

**Export** - PDF report generation with charts, tables, and AI summaries

---

## 1. 🚀 Overview & Motivation

- **Feature Name:** Analyst Dashboard (Next.js/React)
- **Goal:** Provide a high-performance, interactive, and aesthetically premium web interface for match analysis.
- **Problem Solved:** Moving beyond Python-based UIs to enable complex interactions (video scrubbing + canvas drawing + simultaneous chart updates) with a production-grade decoupled architecture.

---

## 2. 🏗️ Architecture Overview

```
┌──────────────────────────────────────┐
│   01. Dashboard Infrastructure       │
│   (Next.js, Zustand, TanStack Query) │
└────────────┬─────────────────────────┘
             │
    ┌────────┴─────┬─────────┬─────────┬─────────┐
    │              │         │         │         │
┌───▼────┐  ┌──▼──┐  ┌──▼──┐  ┌──▼──┐  ┌───▼───┐
│02.Video│  │03.  │  │04.  │  │05.  │  │06.    │
│ Player │  │Pitch│  │Metrics│ │Chat │  │Report │
└────────┘  └─────┘  └──────┘  └─────┘  └───────┘
```

---

## 3. 🔗 Integration Points

### Backend API

- **Base URL:** `http://localhost:8000/api/v1`
- **Key Endpoints:**
  - `/matches` - Match listing
  - `/matches/{id}/tracking` - Player positions
  - `/matches/{id}/metrics` - Tactical metrics
  - `/chat/analyze` - AI analysis (see [Agentic Reasoning](../agentic_reasoning/agentic_reasoning_spec.md))

### State Synchronization

- **Video ↔ Pitch:** `currentTimestamp` in Zustand store
- **Metrics Filtering:** Period selection affects all charts

---

## 4. 📁 Folder Structure

Each spec has its own folder where you can add implementation plans:

```
features/ui_dashboard/
├── ui_dashboard_spec.md (this file)
├── 01_dashboard_infrastructure/
│   ├── 01_dashboard_infrastructure_spec.md
│   └── (future: plan.md)
├── 02_video_player/
│   ├── 02_video_player_spec.md
│   └── (future: plan.md)
├── 03_pitch_visualization/
│   ├── 03_pitch_visualization_spec.md
│   └── (future: plan.md)
├── 04_metrics_dashboard/
│   ├── 04_metrics_dashboard_spec.md
│   └── (future: plan.md)
├── 05_chat_interface/
│   ├── 05_chat_interface_spec.md
│   └── (future: plan.md)
└── 06_reporting/
    ├── 06_reporting_spec.md
    └── (future: plan.md)
```

---

## 5. ✅ Getting Started

**Follow the numbered order (01 → 06):**

1. Start with **01_dashboard_infrastructure** - This establishes the foundation
2. Build **02_video_player** - Core playback functionality
3. Add **03_pitch_visualization** - Sync with video
4. Implement **04_metrics_dashboard** - Statistical analysis
5. Integrate **05_chat_interface** - AI capabilities
6. Complete **06_reporting** - Export functionality

---

## 6. 🔗 References

- [Next.js Documentation](https://nextjs.org/docs)
- [Shadcn/UI](https://ui.shadcn.com/)
- [TanStack Query](https://tanstack.com/query/latest)
