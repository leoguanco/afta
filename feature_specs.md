# ✨ Feature Specification: Software de Análisis de Fútbol con IA

## 1. 🚀 Overview & Motivation

- **Feature Name:** Football Intelligence Engine (FIE)
- **Goal:** To build a hybrid system (Video + Data + LLM) capable of automatically detecting game patterns and generating actionable tactical analysis.

> **📚 Detailed Specifications:**
>
> - [Infrastructure](specs/infrastructure_spec.md) - Docker, DB, API.
> - [Data Ingestion](specs/data_ingestion_spec.md) - StatsBomb, Metrica, External Data.
> - [Object Tracking](specs/object_tracking_spec.md) - YOLOv8, ByteTrack, Video Pipeline.
> - [Pitch Calibration](specs/pitch_calibration_spec.md) - Homography, Keypoints, 2D->3D Mapping.
> - [Tactical Metrics](specs/tactical_metrics_spec.md) - Math Models (Pitch Control, xT, PPDA).
> - [Agentic Reasoning](specs/agentic_reasoning_spec.md) - RAG, CrewAI, LLM Analysis.
> - [UI Dashboard](specs/ui_dashboard_spec.md) - Streamlit, Visualizations, Reporting.

- **Problem Solved (The "Why"):** Tactical analysis is traditionally fragmented between video scouting (qualitative) and data analytics (quantitative). This system unifies them, automating the "grunt work" of tracking and tagging, and uses Generative AI to synthesize complex patterns into readable reports for coaches and analysts.
- **Scope:**
  - **In Scope:**
    - **Ingestion:** Video (MP4) and Event Data (StatsBomb/Metrica).
    - **Computer Vision:** YOLOv8 (Detection) + ByteTrack (Tracking) + Homography (2D to 3D mapping).
    - **Tactical Metrics:** Calculation of xG, PPDA, Compactness, and Space Control.
    - **AI/ML:** Clustering for game phases (Attack/Defense), RAG pipeline for context, and LLM for narrative generation.
    - **Output:** Streamlit Dashboard and PDF/JSON Reports.
  - **Out of Scope:** Real-time live broadcast streaming (sub-second latency), edge device optimization (mobile), biomechanical injury analysis.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Video Analyst**, I want to **upload match footage**, so that **I can get automated player tracking data without manual input.**

| Criteria ID | Acceptance Criteria                                                                                       | Status |
| :---------- | :-------------------------------------------------------------------------------------------------------- | :----- |
| US1.1       | The system SHALL accept video files and generate a standard trajectory file (Frame, ID, X, Y).            | [ ]    |
| US1.2       | The system SHALL use YOLOv8 to detect Players, Referees, and the Ball.                                    | [ ]    |
| US1.3       | The system SHALL implement Homography to transform video pixels to real-world pitch coordinates (meters). | [ ]    |
| US1.4       | The system SHALL track objects consistently across frames using ByteTrack, minimizing ID switches.        | [ ]    |

### **User Story 2:** As a **Tactical Scout**, I want to **see advanced tactical metrics visualizations**, so that **I can evaluate tea structure.**

| Criteria ID | Acceptance Criteria                                                                        | Status |
| :---------- | :----------------------------------------------------------------------------------------- | :----- |
| US2.1       | The system SHALL calculate and visualize "Compactness" (team spread/convex hull).          | [ ]    |
| US2.2       | The system SHALL visualize "Pitch Control" or "Dominance Zones".                           | [ ]    |
| US2.3       | The system SHALL compute PPDA (Passes Per Defensive Action) to measure pressing intensity. | [ ]    |

### **User Story 3:** As a **Head Coach**, I want **a written summary of the match analysis**, so that **I don't have to interpret raw data graphs.**

| Criteria ID | Acceptance Criteria                                                                                                                       | Status |
| :---------- | :---------------------------------------------------------------------------------------------------------------------------------------- | :----- |
| US3.1       | The system SHALL use a RAG (Retrieval-Augmented Generation) pipeline to query match data.                                                 | [ ]    |
| US3.2       | The system SHALL generate a simplified text report describing key game phases (e.g., "Weakness in transition defense on the left flank"). | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture (End-to-End)**

The system follows a linear pipeline:

```mermaid
graph LR
    A[Video / Events] --> B(Ingestion)
    B --> C{Video Processor}
    C -->|YOLO + ByteTrack| D[Tracking Data (x,y,t)]
    D --> E[Feature Extraction]
    E -->|Metrics: xG, PPDA| F[ML Analysis]
    F -->|Clustering| G[Patterns/Phases]
    G --> H[RAG + LLM]
    H --> I[Dashboard / PDF Report]
```

### **3.2 Component Details**

- **Ingestion:**
  - Handlers for MP4 video loading.
  - Parsers for structured data (StatsBomb JSON, Metrica CSV).
- **Video Processor (CV):**
  - `Detector`: Ultralytics YOLOv8.
  - `Tracker`: ByteTrack.
  - `Mapper`: OpenCV Homography matrix calculation based on pitch markings.
- **Feature Extractor:**
  - Logic to sync Event data with Tracking data.
  - Calculation of physical metrics: Speed, Distance, Team Centroids.
- **ML Engine:**
  - Scikit-learn/PyTorch for clustering game phases (e.g., classifying "High Press" vs "Low Block").
- **Intelligence Layer (RAG/LLM):**
  - Vector Store (FAISS/Chroma) to index game events.
  - LangChain to connect statistical summaries with an LLM (OpenAI/Gemini/Llama) for text generation.

### **3.3 Roadmap (based on 8-week Plan)**

1.  **Weeks 1-2:** Setup & Vision Engine. Implement object detection and basic tracking.
2.  **Weeks 3-4:** Data Integration. Build Homography module and ingest StatsBomb/Metrica data.
3.  **Weeks 5-6:** Advanced Analytics. Calculate PPDA, xT, and implement clustering for game phases.
4.  **Weeks 7-8:** RAG & Reporting. Build the Agentic LLM pipeline and the Streamlit dashboard.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - **Computation:** Heavy reliance on GPU (CUDA) for video processing.
  - **Data Rights:** Must respect licensing for any third-party datasets (StatsBomb Open Data).
- **Assumptions:**
  - Video footage provides a sufficiently wide angle to identify at least 4 pitch landmarks for homography.
- **Edge Cases:**
  - **Partial Visibility:** If the camera zooms in too much, homography may fail—system needs a fallback or manual calibration prompt.
  - **Jersey Clashes:** Detection may struggle if teams have similar kit colors; fine-tuning or color histogram analysis might be needed.

---

## 5. 🧪 Testing & Validation Plan

- **Vision Metrics:**
  - **mAP@0.5:** For object (player/ball) detection accuracy.
  - **MOTA / IDF1:** For tracking consistency and ID persistence.
  - **RMSE:** Root Mean Square Error for homography projection accuracy (in meters).
- **Tactical Validation:**
  - Compare calculated metrics (e.g., number of passes, possession %) against ground-truth match reports.
- **User Validation:**
  - Review LLM-generated reports with a football expert to ensure terminology is correct (e.g., not saying "kick" when "cross" is appropriate).

---

## 6. 🔗 References and Related Documentation

- **Theory:** _Soccermatics_ (David Sumpter), _Juego de Posición_ (Óscar Cano).
- **Datasets:** StatsBomb Open Data, Metrica Sports Sample Data.
- **Tools:** [Ultralytics YOLOv8](https://docs.ultralytics.com/), [LangChain](https://python.langchain.com/), [Streamlit](https://streamlit.io/).
