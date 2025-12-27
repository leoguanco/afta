# 💻 Feature Spec: Dashboard & Reporting (UI)

## 1. 🚀 Overview

The **Dashboard** is the user-facing layer. It allows users to upload videos, configure analysis parameters, visualize data on an interactive pitch, and download final reports.

**Goal:** An intuitive, low-latency interface for coaches and analysts.

---

## 2. 🏗️ Technical Architecture

### 2.1 Tech Stack

- **Framework:** Streamlit (Python).
- **Plotting:** `mplsoccer` (Matplotlib wrapper) and `Plotly` (Interactive).
- **Media:** Native Streamlit video player with overlay support (drawing lines on canvas).

### 2.2 UI Layout

1.  **Sidebar (Controls):**
    - File Upload (Video/Event Data).
    - Team Configuration (Colors, Names).
    - Analysis Mode (Full Match / Clip / set-piece).
    - "Generate Report" Button.
2.  **Main View (Tabs):**
    - **Tab 1: Video Player:** Playback with overlaid tracking bounding boxes.
    - **Tab 2: Pitch View:** 2D Top-down animation of player dots + Voronoi diagrams / Pitch Control heatmaps.
    - **Tab 3: Metrics:** Time-series charts (e.g., PPDA over 90 mins).
    - **Tab 4: AI Chat:** Chatbot interface to query the match data.

---

## 3. 📝 Reporting

### 3.1 PDF Export

- **Library:** `xhtml2pdf` or `ReportLab`.
- **Structure:**
  - Header (Match Info).
  - Executive Summary (LLM generated).
  - Key Stats Table.
  - Visualizations (Static Images of Heatmaps).
  - Recommendations.

---

## 4. ⚙️ Configuration

- **Performance:** Streamlit caching (`@st.cache_data`) for heavy computations (tracking calculation).
- **Theme:** Dark mode by default (better for video analysis).

---

## 5. ✅ Acceptance Criteria

| ID        | Criteria                                                  | Test Method       |
| :-------- | :-------------------------------------------------------- | :---------------- |
| **UI-01** | Render top-down pitch view at >15 FPS.                    | Browser Profiling |
| **UI-02** | Allow filtering heatmaps by "First Half" / "Second Half". | Functional Test   |
| **UI-03** | Chat interface responds to user queries within 5s.        | Latency Check     |
| **UI-04** | PDF Report contains at least 2 graphs and 1 text summary. | Output Inspection |
