# ✨ Feature Specification: UI Dashboard & Reporting

> **Context:** This is the main specification document for the UI Dashboard feature. For detailed component specifications, see the individual spec files listed below.

## 📑 Modular Specifications

The UI Dashboard has been divided into the following component specifications:

### Core Infrastructure

- **[Dashboard Infrastructure](./dashboard_infrastructure_spec.md)** - Foundation (Next.js, routing, state management, API client, design system)

### UI Components

- **[Video Player](./video_player_spec.md)** - Video playback with drawing overlay
- **[Pitch Visualization](./pitch_visualization_spec.md)** - Interactive 2D pitch view with heatmaps
- **[Metrics Dashboard](./metrics_dashboard_spec.md)** - Time-series charts and statistics
- **[Chat Interface](./chat_interface_spec.md)** - AI-powered match analysis chat
- **[Reporting](./reporting_spec.md)** - PDF report generation

---

## 1. � Overview & Motivation

- **Feature Name:** Analyst Dashboard (Next.js/React)
- **Goal:** Provide a high-performance, interactive, and aesthetically premium web interface for match analysis.
- **Problem Solved:** Moving beyond Python-based UIs to enable complex interactions (video scrubbing + canvas drawing + simultaneous chart updates) with a production-grade decoupled architecture.

---

## 2. 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│         Dashboard Infrastructure         │
│  (Next.js, Zustand, TanStack Query)     │
└───────────┬─────────────────────────────┘
            │
    ┌───────┴────────┬────────────┬────────────┬──────────┐
    │                │            │            │          │
┌───▼────┐  ┌───▼────┐  ┌───▼────┐  ┌───▼────┐  ┌───▼────┐
│ Video  │  │ Pitch  │  │Metrics │  │  Chat  │  │Report  │
│ Player │  │  View  │  │ Charts │  │Interface│  │Generator│
└────────┘  └────────┘  └────────┘  └────────┘  └────────┘
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

## 4. ✅ Getting Started

To implement this feature, follow these steps:

1. **Start with Infrastructure:** Implement [Dashboard Infrastructure](./dashboard_infrastructure_spec.md) first
2. **Build Components in Order:**
   - [Video Player](./video_player_spec.md) - Core playback
   - [Pitch Visualization](./pitch_visualization_spec.md) - Sync with video
   - [Metrics Dashboard](./metrics_dashboard_spec.md) - Data display
   - [Chat Interface](./chat_interface_spec.md) - AI integration
   - [Reporting](./reporting_spec.md) - Export functionality

---

## 5. 🔗 References

- [Next.js Documentation](https://nextjs.org/docs)
- [Shadcn/UI](https://ui.shadcn.com/)
- [TanStack Query](https://tanstack.com/query/latest)
