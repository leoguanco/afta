# ⚽ Football Intelligence Engine (AFTA)

> **Automated Football Tactical Analysis** - Combining Computer Vision, Advanced Analytics, and Generative AI.

---

## 📐 Architecture Overview

- **Backend:** Python 3.10+ (FastAPI), **Hexagonal Architecture**, Celery Workers.
- **Frontend:** Next.js 14 (TypeScript), Shadcn/UI, TailwindCSS.
- **Database:** PostgreSQL 16 (PostGIS, pgvector).
- **Infrastructure:** Docker Compose, Redis, MinIO, Prometheus, Grafana.

### Service Architecture

| Service      | Purpose                            | Queue       | Dependencies                      |
| ------------ | ---------------------------------- | ----------- | --------------------------------- |
| `api`        | HTTP endpoints (FastAPI)           | -           | Minimal (FastAPI, DB, Redis)      |
| `worker-cpu` | Data ingestion, CrewAI analysis    | `default`   | Full ML stack (CrewAI, LangChain) |
| `worker-gpu` | Video processing (YOLO, ByteTrack) | `gpu_queue` | CUDA, PyTorch, OpenCV             |

---

## 🔌 API Endpoints

| Endpoint                        | Method | Purpose                              | Worker     |
| ------------------------------- | ------ | ------------------------------------ | ---------- |
| `/health`                       | GET    | Real connectivity checks (DB, Redis) | -          |
| `/docs`                         | GET    | OpenAPI documentation                | -          |
| `/metrics`                      | GET    | Prometheus metrics                   | -          |
| `/api/v1/ingest`                | POST   | Start match data ingestion           | worker-cpu |
| `/api/v1/process-video`         | POST   | Start video tracking (YOLO)          | worker-gpu |
| `/api/v1/calibrate`             | POST   | Compute pitch homography             | worker-cpu |
| `/api/v1/calculate-metrics`     | POST   | Calculate tactical metrics           | worker-cpu |
| `/api/v1/chat/analyze`          | POST   | Start AI analysis (CrewAI)           | worker-cpu |
| `/api/v1/chat/jobs/{id}`        | GET    | Poll job status                      | -          |
| `/api/v1/reports/generate`      | POST   | Generate tactical report (PDF/JSON)  | worker-cpu |
| `/api/v1/patterns/detect`       | POST   | Detect tactical patterns             | worker-cpu |
| `/api/v1/matches/{id}/patterns` | GET    | Get discovered patterns              | -          |

---

## Detailed Specifications

| Module                   | Description                                     | Link                                                                                                                                 |
| :----------------------- | :---------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| **Infrastructure**       | Docker, Hexagonal structure, TDD, Observability | [features/01_infrastructure/01_infrastructure_spec.md](features/01_infrastructure/01_infrastructure_spec.md)                         |
| **Data Ingestion**       | StatsBomb, Metrica, Async Workers               | [features/02_data_ingestion/02_data_ingestion_spec.md](features/02_data_ingestion/02_data_ingestion_spec.md)                         |
| **Object Tracking**      | YOLOv8, ByteTrack, Vision Worker                | [features/03_object_tracking/03_object_tracking_spec.md](features/03_object_tracking/03_object_tracking_spec.md)                     |
| **Pitch Calibration**    | Homography, Keypoint Detection                  | [features/04_pitch_calibration/04_pitch_calibration_spec.md](features/04_pitch_calibration/04_pitch_calibration_spec.md)             |
| **Tactical Metrics**     | Pitch Control, xT, PPDA, Physical Load          | [features/05_tactical_metrics/05_tactical_metrics_spec.md](features/05_tactical_metrics/05_tactical_metrics_spec.md)                 |
| **Agentic Reasoning**    | RAG, CrewAI, LLM Analysis                       | [features/06_agentic_reasoning/06_agentic_reasoning_spec.md](features/06_agentic_reasoning/06_agentic_reasoning_spec.md)             |
| **RAG Indexing**         | Vector Store, ChromaDB, Embeddings              | [features/06_agentic_reasoning/06c_rag_indexing_spec.md](features/06_agentic_reasoning/06c_rag_indexing_spec.md)                     |
| **Phase Classification** | ML-based 4-phase game state detection           | [features/07_phase_classification/07_phase_classification_spec.md](features/07_phase_classification/07_phase_classification_spec.md) |
| **Report Generation**    | PDF/JSON export with charts and LLM narrative   | [features/08_report_generation/08_report_generation_spec.md](features/08_report_generation/08_report_generation_spec.md)             |
| **Pattern Detection**    | Unsupervised ML clustering of tactical patterns | [features/09_pattern_detection/09_pattern_detection_spec.md](features/09_pattern_detection/09_pattern_detection_spec.md)             |
| **Event Recognition**    | Heuristic & AI-based event inference from video | [features/10_event_recognition/10_event_recognition_spec.md](features/10_event_recognition/10_event_recognition_spec.md)             |
| **Match Metadata**       | Team names, lineups, video-data sync            | [features/11_match_metadata/11_match_metadata_spec.md](features/11_match_metadata/11_match_metadata_spec.md)                         |
| **Highlight Mode**       | Scene detection, per-clip analysis              | [features/12_highlight_mode/12_highlight_mode_spec.md](features/12_highlight_mode/12_highlight_mode_spec.md)                         |
| **UI Dashboard**         | Next.js, Interactive Pitch, Video Sync          | [features/ui_dashboard/ui_dashboard_spec.md](features/ui_dashboard/ui_dashboard_spec.md)                                             |

---

## Implementation Status

| Feature              | Status         | API Endpoint                  | Notes                          |
| :------------------- | :------------- | :---------------------------- | :----------------------------- |
| Data Ingestion       | 🟢 Implemented | `/api/v1/ingest`              | StatsBomb adapter complete     |
| Object Tracking      | 🟢 Implemented | `/api/v1/process-video`       | YOLO + ByteTrack on GPU worker |
| Pitch Calibration    | 🟢 Implemented | `/api/v1/calibrate`           | OpenCV homography computation  |
| Tactical Metrics     | 🟢 Implemented | `/api/v1/calculate-metrics`   | Rich domain entities           |
| Agentic Reasoning    | 🟢 Implemented | `/api/v1/chat/analyze`        | CrewAI multi-agent system      |
| Health Monitoring    | 🟢 Implemented | `/health`                     | Real DB/Redis connectivity     |
| Phase Classification | 🟢 Implemented | `/api/v1/matches/{id}/phases` | ML 4-phase classification      |
| Report Generation    | 🟢 Implemented | `/api/v1/reports/generate`    | PDF/JSON with mplsoccer charts |
| Pattern Detection    | 🟢 Implemented | `/api/v1/patterns/detect`     | K-means/DBSCAN clustering      |

### Architecture Improvements (Recent)

- ✅ **Hexagonal Architecture** - Ports & Adapters pattern
- ✅ **Dependency Separation** - `requirements-api.txt` vs `requirements-worker.txt`
- ✅ **Test Doubles** - Fakes instead of `mock.patch` (see `tests/fakes.py`)
- ✅ **Lazy Task Dispatch** - API uses `send_task()` to avoid importing heavy deps
- ✅ **Real Health Checks** - DB and Redis connectivity verified

---

## 🚀 Quick Start

```bash
# Clone & Start
git clone <repo>
cd afta
docker-compose up -d --build

# Access
# Dashboard: http://localhost:3000
# API Docs:  http://localhost:8000/docs
# Health:    http://localhost:8000/health
```

### Initialize Database (First Time)

```bash
# Set environment and run init script
$env:DATABASE_URL='postgresql://postgres:postgres@localhost:5432/afta'
python -m src.infrastructure.db.init_db
```

### Run Tests

```bash
cd backend
pytest tests/ -v
```

---

## 📁 Project Structure

```
afta/
├── backend/
│   ├── src/
│   │   ├── domain/           # Entities, Value Objects, Ports
│   │   ├── application/      # Use Cases
│   │   └── infrastructure/   # Adapters, API, Workers
│   ├── tests/
│   │   └── fakes.py          # Test doubles
│   ├── docker/
│   │   ├── Dockerfile.api    # Minimal deps (FastAPI)
│   │   ├── Dockerfile.worker # Full ML stack
│   │   └── Dockerfile.gpu    # CUDA + PyTorch
│   ├── requirements-api.txt
│   └── requirements-worker.txt
├── frontend/
├── docker-compose.yml
└── feature_specs.md          # This file
```

---

## 📚 References

- [README.md](README.md) - Full project documentation
- [GPU_WORKER.md](backend/GPU_WORKER.md) - GPU worker architecture
- [StatsBomb Open Data](https://github.com/statsbomb/open-data)
- [Metrica Sports Sample Data](https://github.com/metrica-sports/sample-data)
