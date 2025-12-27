# 🧠 Feature Spec: Tactical Intelligence (Analysis & AI)

## 1. 🚀 Overview

The **Tactical Intelligence** module is the "brain" of the system. It ingests raw tracking/event data, computes advanced metrics, and uses Generative AI to produce natural language insights.

**Goal:** Turn numbers into narrative.

---

## 2. 🏗️ Technical Architecture

### 2.1 Metric Engine (Python)

- **Physical Metrics:**
  - `Speed/Acceleration`: First/Second derivatives of position.
  - `Distance Covered`: Aggregate movement.
  - `Metabolic Power`: Energy expenditure estimation.
- **Tactical Metrics:**
  - `Team Centroid`: Average position of all outfield players.
  - `Convex Hull`: Area covered by the team (Compactness).
  - `Inter-Team Distance`: Distance between team centroids (Line Height).
  - `Pitch Control`: Probability field of controlling the ball at any point $(x,y)$ (using Spearman's model).
- **Event Metrics (if Event Data available):**
  - `PPDA` (Passes Allowed Per Defensive Action): Pressing intensity.
  - `xG` (Expected Goals): Shot quality model.
  - `xT` (Expected Threat): Value of moving the ball to specific zones.

### 2.2 AI Layer (RAG pipeline)

1.  **Context Construction:**
    - Convert computed metrics into text snippets.
    - _Example:_ "Minute 15-30: Team A Pressing Intensity = High (PPDA 6.5). Team B Loss of Possession = 4x in Defensive Third."
2.  **Indexing:**
    - Store snippets in a Vector Database (FAISS/Chroma).
3.  **Agent Roles (CrewAI/LangChain):**
    - **Data Analyst Agent:** Queries the database for stats.
    - **Tactical Scout Agent:** Interprets stats (e.g., "High PPDA means aggressive pressing").
    - **Writer Agent:** Drafts the final report.

---

## 3. 📝 Data Schemas

### 3.1 Metrics Record

| Field                | Type   | Description                            |
| :------------------- | :----- | :------------------------------------- |
| `window_start`       | int    | Start frame of analysis window         |
| `window_end`         | int    | End frame                              |
| `team_a_compactness` | float  | Avg $m^2$ covered                      |
| `team_b_ppda`        | float  | Pressing index                         |
| `dominant_zone`      | string | 'Left Flank', 'Central', 'Right Flank' |

---

## 4. ⚙️ Configuration

- **Models:**
  - **LLM:** GPT-4o (recommended) or Llama-3-70b (local alternative).
  - **Pitch Control:** Pre-trained weights or heuristic-based (speed/distance decay).

---

## 5. ✅ Acceptance Criteria

| ID        | Criteria                                                               | Test Method         |
| :-------- | :--------------------------------------------------------------------- | :------------------ |
| **TI-01** | Compute Team Centroids for >95% of tracked frames.                     | Unit Test           |
| **TI-02** | RAG system retrieves correct context for "How did we defend corners?". | Manual Query Eval   |
| **TI-03** | Generate a text summary < 500 words for a match half.                  | Output Length Check |
