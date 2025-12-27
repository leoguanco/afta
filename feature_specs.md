# ⚽ Football Intelligence Engine (AFTA)

> **Automated Football Tactical Analysis** - Combining Computer Vision, Advanced Analytics, and Generative AI.

---

## 📐 Architecture Overview

- **Backend:** Python 3.11+ (FastAPI), **Hexagonal Architecture**, Celery Workers.
- **Frontend:** Next.js 14 (TypeScript), Shadcn/UI, TailwindCSS.
- **Database:** PostgreSQL 16 (PostGIS, pgvector).
- **Infrastructure:** Docker Compose, Redis, MinIO, Prometheus, Grafana.

---

## � Detailed Specifications

| Module                | Description                                     | Link                                                               |
| :-------------------- | :---------------------------------------------- | :----------------------------------------------------------------- |
| **Infrastructure**    | Docker, Hexagonal structure, TDD, Observability | [specs/infrastructure_spec.md](specs/infrastructure_spec.md)       |
| **Data Ingestion**    | StatsBomb, Metrica, Async Workers               | [specs/data_ingestion_spec.md](specs/data_ingestion_spec.md)       |
| **Object Tracking**   | YOLOv8, ByteTrack, Vision Worker                | [specs/object_tracking_spec.md](specs/object_tracking_spec.md)     |
| **Pitch Calibration** | Homography, Keypoint Detection                  | [specs/pitch_calibration_spec.md](specs/pitch_calibration_spec.md) |
| **Tactical Metrics**  | Pitch Control, xT, PPDA, Physical Load          | [specs/tactical_metrics_spec.md](specs/tactical_metrics_spec.md)   |
| **Agentic Reasoning** | RAG, CrewAI, LLM Analysis                       | [specs/agentic_reasoning_spec.md](specs/agentic_reasoning_spec.md) |
| **UI Dashboard**      | Next.js, Interactive Pitch, Video Sync          | [specs/ui_dashboard_spec.md](specs/ui_dashboard_spec.md)           |

---

## Implementation Plans

| Feature           | Status         | Link                                                               |
| :---------------- | :------------- | :----------------------------------------------------------------- |
| Data Ingestion    | Implemented    | [plans/data_ingestion_plan.md](plans/data_ingestion_plan.md)       |
| Object Tracking   | 🟢 Implemented | [plans/object_tracking_plan.md](plans/object_tracking_plan.md)     |
| Pitch Calibration | 🟢 Implemented | [plans/pitch_calibration_plan.md](plans/pitch_calibration_plan.md) |

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
# Flower:    http://localhost:5555
```

---

## � References

- [README.md](README.md) - Full project documentation.
- [StatsBomb Open Data](https://github.com/statsbomb/open-data)
- [Metrica Sports Sample Data](https://github.com/metrica-sports/sample-data)
