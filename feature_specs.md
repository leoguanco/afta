# ⚽ Football Intelligence Engine (AFTA)

> **Automated Football Tactical Analysis** - Combining Computer Vision, Advanced Analytics, and Generative AI.

---

## 📐 Architecture Overview

- **Backend:** Python 3.11+ (FastAPI), **Hexagonal Architecture**, Celery Workers.
- **Frontend:** Next.js 14 (TypeScript), Shadcn/UI, TailwindCSS.
- **Database:** PostgreSQL 16 (PostGIS, pgvector).
- **Infrastructure:** Docker Compose, Redis, MinIO, Prometheus, Grafana.

---

## Detailed Specifications

| Module                | Description                                     | Link                                                                                                                                                                                                                   |
| :-------------------- | :---------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Infrastructure**    | Docker, Hexagonal structure, TDD, Observability | [features/infrastructure/infrastructure_spec.md](features/infrastructure/infrastructure_spec.md)                                                                                                                       |
| **Data Ingestion**    | StatsBomb, Metrica, Async Workers               | [features/data_ingestion/data_ingestion_spec.md](features/data_ingestion/data_ingestion_spec.md)                                                                                                                       |
| **Object Tracking**   | YOLOv8, ByteTrack, Vision Worker                | [features/object_tracking/object_tracking_spec.md](features/object_tracking/object_tracking_spec.md)                                                                                                                   |
| **Pitch Calibration** | Homography, Keypoint Detection                  | [features/pitch_calibration/pitch_calibration_spec.md](features/pitch_calibration/pitch_calibration_spec.md)                                                                                                           |
| **Tactical Metrics**  | Pitch Control, xT, PPDA, Physical Load          | [features/tactical_metrics/tactical_metrics_spec.md](features/tactical_metrics/tactical_metrics_spec.md) <br> [features/tactical_metrics/tactical_metrics_plan.md](features/tactical_metrics/tactical_metrics_plan.md) |
| **Agentic Reasoning** | RAG, CrewAI, LLM Analysis                       | [features/agentic_reasoning/agentic_reasoning_spec.md](features/agentic_reasoning/agentic_reasoning_spec.md)                                                                                                           |
| **UI Dashboard**      | Next.js, Interactive Pitch, Video Sync          | [features/ui_dashboard/ui_dashboard_spec.md](features/ui_dashboard/ui_dashboard_spec.md)                                                                                                                               |

---

## Implementation Plans

| Feature           | Status         | Link                                                                                                         |
| :---------------- | :------------- | :----------------------------------------------------------------------------------------------------------- |
| Data Ingestion    | 🟢 Implemented | [features/data_ingestion/data_ingestion_plan.md](features/data_ingestion/data_ingestion_plan.md)             |
| Object Tracking   | 🟢 Implemented | [features/object_tracking/object_tracking_plan.md](features/object_tracking/object_tracking_plan.md)         |
| Pitch Calibration | 🟢 Implemented | [features/pitch_calibration/pitch_calibration_plan.md](features/pitch_calibration/pitch_calibration_plan.md) |
| Tactical Metrics  | 🟢 Implemented | [features/tactical_metrics/tactical_metrics_plan.md](features/tactical_metrics/tactical_metrics_plan.md)     |

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
