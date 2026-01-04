# ⚽ Football Intelligence Engine (AFTA)

> **Automated Football Tactical Analysis** powered by Computer Vision, Large Language Models, and Advanced Analytics.

## 📖 Overview

The **Football Intelligence Engine** is a comprehensive system designed to ingest match footage, extract player trajectories via Computer Vision (YOLO + ByteTrack), calculate advanced tactical metrics (Pitch Control, xT, PPDA), and generate natural language insights using Agentic AI.

It is built with a **Hexagonal Architecture** to ensure domain purity and uses a **Distributed Asynchronous** design to handle heavy computational loads (GPU Processing, LLM Reasoning).

## ✨ Key Features

| Feature                   | Description                                                |
| ------------------------- | ---------------------------------------------------------- |
| **Video Processing**      | YOLO + ByteTrack object detection and tracking             |
| **Trajectory Smoothing**  | Savitzky-Golay filter for noise reduction                  |
| **Track Cleaning**        | Ghost removal and fragmented track merging                 |
| **Event Recognition**     | Heuristic-based possession, pass, and pressure detection   |
| **Scene Detection**       | Automatic scene cuts for highlight videos                  |
| **Action Classification** | Goal, shot, corner, celebration detection                  |
| **Player Lineup Mapping** | Associate track IDs with real player names                 |
| **RAG Integration**       | ChromaDB for contextual match analysis                     |
| **PPDA Metrics**          | Pressing intensity calculation                             |
| **Time Sync**             | Frame-to-timestamp conversion for StatsBomb data alignment |

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
│   │   │   ├── services/       # TrajectorySmoother, TrackCleaner, SceneDetector
│   │   │   └── ports/          # Repository interfaces (LineupRepository, etc.)
│   │   ├── application/        # Use Cases & Orchestration
│   │   │   └── use_cases/      # VideoProcessor, MetricsCalculator, EventDetector
│   │   └── infrastructure/     # Adapters (API, DB, Workers)
│   │       ├── api/endpoints/  # REST endpoints (video, lineup, indexing)
│   │       ├── ml/             # ActionClassifier
│   │       └── vision/         # YOLODetector, ByteTracker, SceneDetector
│   ├── tests/
│   │   └── unit/               # 24 unit tests passing
│   └── docker/
├── frontend/                   # Next.js Frontend
├── features/                   # Feature specifications (10+ specs)
├── docker-compose.yml
└── feature_specs.md
```

## 🔌 API Endpoints

| Endpoint                     | Method | Description                      |
| ---------------------------- | ------ | -------------------------------- |
| `/health`                    | GET    | Real DB/Redis connectivity check |
| `/docs`                      | GET    | OpenAPI documentation            |
| `/api/v1/ingest`             | POST   | Start match data ingestion       |
| `/api/v1/process-video`      | POST   | Start video tracking (GPU)       |
| `/api/v1/calculate-metrics`  | POST   | Calculate tactical metrics       |
| `/api/v1/chat/analyze`       | POST   | Start AI analysis (CrewAI)       |
| `/api/v1/lineups`            | POST   | Set player-track mappings 🆕     |
| `/api/v1/lineups/{match_id}` | GET    | Get lineup for match 🆕          |
| `/api/v1/index/{match_id}`   | POST   | Index match for RAG 🆕           |
| `/api/v1/reports/generate`   | POST   | Generate tactical report         |
| `/api/v1/patterns/detect`    | POST   | Detect tactical patterns         |

### Video Processing Options

```json
POST /api/v1/process-video
{
  "video_path": "/data/match.mp4",
  "output_path": "/output",
  "metadata": {
    "home_team": "Barcelona",
    "away_team": "Real Madrid",
    "date": "2025-01-03",
    "competition": "La Liga"
  },
  "sync_offset_seconds": 300.0,
  "mode": "full_match"  // or "highlights"
}
```

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
   docker exec afta-api python -m src.infrastructure.db.init_db
   ```

4. **Access the applications:**
   - **Dashboard (Frontend):** http://localhost:3000
   - **API Docs (Swagger):** http://localhost:8000/docs
   - **Health Check:** http://localhost:8000/health
   - **MinIO Console:** http://localhost:9001

## 🧪 Testing (TDD)

We enforce **Test Driven Development** with **Hexagonal Architecture** testing patterns.

```bash
# Run all unit tests
docker-compose exec api python -m pytest tests/unit -v

# Current test count: 24 tests passing
```

**Test Coverage:**

- TrajectorySmoother (3 tests)
- TrackCleaner (3 tests)
- HeuristicEventDetector (3 tests)
- TimeSync (6 tests)
- ActionClassifier (4 tests)
- SceneDetector (3 tests)
- Lineup utilities (2 tests)

## 📜 Documentation

Detailed specifications for each module:

- [Feature Specs](feature_specs.md) - Complete API and architecture reference
- [GPU Worker](backend/GPU_WORKER.md) - Vision processing architecture

Feature specifications in `features/` directory:

| Feature              | Spec                                                                                        |
| -------------------- | ------------------------------------------------------------------------------------------- |
| Infrastructure       | [01_infrastructure](features/01_infrastructure/01_infrastructure_spec.md)                   |
| Data Ingestion       | [02_data_ingestion](features/02_data_ingestion/02_data_ingestion_spec.md)                   |
| Object Tracking      | [03_object_tracking](features/03_object_tracking/03_object_tracking_spec.md)                |
| Pitch Calibration    | [04_pitch_calibration](features/04_pitch_calibration/04_pitch_calibration_spec.md)          |
| Tactical Metrics     | [05_tactical_metrics](features/05_tactical_metrics/05_tactical_metrics_spec.md)             |
| Agentic Reasoning    | [06_agentic_reasoning](features/06_agentic_reasoning/06_agentic_reasoning_spec.md)          |
| Phase Classification | [07_phase_classification](features/07_phase_classification/07_phase_classification_spec.md) |
| Report Generation    | [08_report_generation](features/08_report_generation/08_report_generation_spec.md)          |
| Pattern Detection    | [09_pattern_detection](features/09_pattern_detection/09_pattern_detection_spec.md)          |
| Event Recognition    | [10_event_recognition](features/10_event_recognition/10_event_recognition_spec.md) 🆕       |
| Match Metadata       | [11_match_metadata](features/11_match_metadata/11_match_metadata_spec.md) 🆕                |
| Highlight Mode       | [12_highlight_mode](features/12_highlight_mode/12_highlight_mode_spec.md) 🆕                |

---

**License:** MIT  
**Maintainer:** Leo Guanco
