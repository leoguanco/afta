# ⚽ Football Intelligence Engine (AFTA)

> **Automated Football Tactical Analysis** powered by Computer Vision, Large Language Models, and Advanced Analytics.

## 📖 Overview

The **Football Intelligence Engine** is a comprehensive system designed to ingest match footage, extract player trajectories via Computer Vision (YOLO + ByteTrack), calculate advanced tactical metrics (Pitch Control, xT, PPDA), and generate natural language insights using Agentic AI.

It is built with a **Hexagonal Architecture** to ensure domain purity and uses a **Distributed Asynchronous** design to handle heavy computational loads (GPU Processing, LLM Reasoning).

## 🏗️ Architecture Stack

- **Backend:** Python 3.10+, FastAPI (REST API), Celery (Async Workers).
- **Frontend:** Next.js 14 (App Router), TypeScript, Shadcn/UI, TailwindCSS.
- **Database:** PostgreSQL 16 (w/ PostGIS & pgvector).
- **AI/ML:**
  - **Vision:** YOLOv8, ByteTrack, OpenCV.
  - **Reasoning:** CrewAI, LangChain, ChromaDB (RAG).
- **Infrastructure:** Docker Compose, Redis, MinIO (S3 Object Storage).

### Service Architecture

| Service      | Purpose                                  | Queue       |
| ------------ | ---------------------------------------- | ----------- |
| `api`        | HTTP REST endpoints                      | -           |
| `worker-cpu` | Data ingestion, CrewAI analysis, metrics | `default`   |
| `worker-gpu` | Video processing (YOLO + ByteTrack)      | `gpu_queue` |

## 📂 Project Structure

```bash
afta/
├── backend/                    # Python Backend
│   ├── src/
│   │   ├── domain/             # Pure Business Logic (Hexagonal Core)
│   │   ├── application/        # Use Cases & Orchestration
│   │   └── infrastructure/     # Adapters (API, DB, Workers)
│   ├── tests/
│   │   └── fakes.py            # Test doubles (Hexagonal testing)
│   ├── docker/
│   │   ├── Dockerfile.api      # Minimal deps for API
│   │   ├── Dockerfile.worker   # Full ML stack for workers
│   │   └── Dockerfile.gpu      # CUDA + PyTorch for vision
│   ├── requirements-api.txt    # API dependencies
│   └── requirements-worker.txt # Worker dependencies
├── frontend/                   # Next.js Frontend
│   ├── app/                    # App Router Pages
│   └── components/             # Shadcn UI Components
├── docker-compose.yml          # All services configuration
└── feature_specs.md            # Feature specifications
```

## 🔌 API Endpoints

| Endpoint                        | Method | Description                      |
| ------------------------------- | ------ | -------------------------------- |
| `/health`                       | GET    | Real DB/Redis connectivity check |
| `/docs`                         | GET    | OpenAPI documentation            |
| `/api/v1/ingest`                | POST   | Start match data ingestion       |
| `/api/v1/process-video`         | POST   | Start video tracking (GPU)       |
| `/api/v1/calibrate`             | POST   | Compute pitch homography         |
| `/api/v1/calculate-metrics`     | POST   | Calculate tactical metrics       |
| `/api/v1/chat/analyze`          | POST   | Start AI analysis (CrewAI)       |
| `/api/v1/chat/jobs/{id}`        | GET    | Poll job status                  |
| `/api/v1/reports/generate`      | POST   | Generate tactical report         |
| `/api/v1/patterns/detect`       | POST   | Detect tactical patterns         |
| `/api/v1/matches/{id}/patterns` | GET    | Get discovered patterns          |

## 🚀 Quick Start (Local Development)

### Prerequisites

- **Docker Desktop** (running)
- **NVIDIA Drivers** (optional, for GPU acceleration)
- **Python 3.10+** & **Node.js 18+**

### Running the Stack

1. **Clone the repository:**

   ```bash
   git clone https://github.com/leoguanco/afta.git
   cd afta
   ```

2. **Start all services:**

   ```bash
   docker-compose up -d --build
   ```

3. **Initialize database (first time only):**

   ```bash
   # From host machine
   docker exec afta-api python -m src.infrastructure.db.init_db
   ```

4. **Access the applications:**
   - **Dashboard (Frontend):** http://localhost:3000
   - **API Docs (Swagger):** http://localhost:8000/docs
   - **Health Check:** http://localhost:8000/health
   - **MinIO Console:** http://localhost:9001

## 🧪 Testing (TDD)

We enforce **Test Driven Development** with **Hexagonal Architecture** testing patterns.

- **Backend Tests:**

  ```bash
  cd backend
  pytest tests/unit -v
  ```

- **Production Verification (E2E):** (Requires Docker running)

  ```bash
  # Run full system verification (Ingestion -> DB -> Reports)
  docker exec -e E2E_API_URL=http://localhost:8000 afta-api pytest tests/e2e -v
  ```

- **Test Architecture:**
  - Uses **Fake implementations** instead of `mock.patch`
  - See `tests/fakes.py` for `FakeMatchRepository`, `FakeStorageAdapter`, etc.
  - 10/10 tests passing

## 📜 Documentation

Detailed specifications for each module:

- [Feature Specs](feature_specs.md) - Complete API and architecture reference
- [GPU Worker](backend/GPU_WORKER.md) - Vision processing architecture

Feature specifications in `features/` directory:

- [Infrastructure](features/01_infrastructure/01_infrastructure_spec.md)
- [Data Ingestion](features/02_data_ingestion/02_data_ingestion_spec.md)
- [Object Tracking](features/03_object_tracking/03_object_tracking_spec.md)
- [Pitch Calibration](features/04_pitch_calibration/04_pitch_calibration_spec.md)
- [Tactical Metrics](features/05_tactical_metrics/05_tactical_metrics_spec.md)
- [Agentic Reasoning](features/06_agentic_reasoning/06_agentic_reasoning_spec.md)
- [Phase Classification](features/07_phase_classification/07_phase_classification_spec.md) 🆕
- [Report Generation](features/08_report_generation/08_report_generation_spec.md) 🆕
- [Pattern Detection](features/09_pattern_detection/09_pattern_detection_spec.md) 🆕
- [Design Specs](features/ui_dashboard/ui_dashboard_spec.md)
- [Architecture & Flow Diagrams](docs/architecture_diagrams.md) 🆕

---

**License:** MIT  
**Maintainer:** Leo Guanco
