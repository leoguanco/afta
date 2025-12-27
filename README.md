# ⚽ Football Intelligence Engine (AFTA)

> **Automated Football Tactical Analysis** powered by Computer Vision, Large Language Models, and Advanced Analytics.

## 📖 Overview

The **Football Intelligence Engine** is a comprehensive system designed to ingest match footage, extract player trajectories via Computer Vision (YOLO + ByteTrack), calculate advanced tactical metrics (Pitch Control, xT, PPDA), and generate natural language insights using Agentic AI.

It is built with a **Hexagonal Architecture** to ensure domain purity and uses a **Distributed Asynchronous** design to handle heavy computational loads (GPU Processing, LLM Reasoning).

## 🏗️ Architecture Stack

- **Backend:** Python 3.11+, FastAPI (REST API), Celery (Async Workers).
- **Frontend:** Next.js 14 (App Router), TypeScript, Shadcn/UI, TailwindCSS.
- **Database:** PostgreSQL 16 (w/ PostGIS & pgvector).
- **AI/ML:**
  - **Vision:** YOLOv8, ByteTrack, OpenCV.
  - **Reasoning:** CrewAI, LangChain, ChromaDB (RAG).
- **Infrastructure:** Docker Compose, Redis, MinIO (S3 Object Storage).

## 📂 Project Structure

```bash
afta/
├── backend/                # Python Backend
│   ├── src/
│   │   ├── domain/         # Pure Business Logic (Hexagonal Core)
│   │   ├── application/    # Use Cases & Orchestration
│   │   └── infrastructure/ # Adapters (API, DB, External Libs)
│   └── tests/              # TDD Suite (Pytest)
├── frontend/               # Next.js Frontend
│   ├── app/                # App Router Pages
│   └── components/         # Shadcn UI Components
└── docker/                 # Container Configurations
```

## 🚀 Quick Start (Local Development)

### Prerequisites

- **Docker Desktop** (running)
- **NVIDIA Drivers** (if using GPU acceleration)
- **Python 3.11+** & **Node.js 18+**

### Running the Stack

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/leoguanco/afta.git
    cd afta
    ```

2.  **Start all services:**

    ```bash
    docker-compose up -d --build
    ```

3.  **Access the applications:**
    - **Dashboard (Frontend):** [http://localhost:3000](http://localhost:3000)
    - **API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
    - **Task Monitor (Flower):** [http://localhost:5555](http://localhost:5555)
    - **MinIO Console:** [http://localhost:9001](http://localhost:9001)

## 🧪 Testing (TDD)

We enforce **Test Driven Development**. No production code is accepted without tests.

- **Backend Tests:**
  ```bash
  docker-compose exec api pytest
  ```
- **Frontend Tests:**
  ```bash
  cd frontend && npm test
  ```

## 📜 Documentation

Detailed specifications for each module can be found in the `specs/` directory:

- [Infrastructure](specs/infrastructure_spec.md)
- [Data Ingestion](specs/data_ingestion_spec.md)
- [Object Tracking](specs/object_tracking_spec.md)
- [Tactical Metrics](specs/tactical_metrics_spec.md)
- [Agentic Reasoning](specs/agentic_reasoning_spec.md)
- [UI Dashboard](specs/ui_dashboard_spec.md)

---

**License:** MIT
**Maintainer:** Leo Guanco
