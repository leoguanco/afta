# 🏗️ Architecture & Flow Diagrams

This document visualizes the workflows of the implemented features in the Football Intelligence Engine.

## 1. System Overview (Hexagonal Architecture)

```mermaid
graph TD
    Client["Web/API Client"] --> API["FastAPI (Infrastructure)"]

    subgraph "Application Layer (Use Cases)"
        IngestUC[IngestMatch]
        VideoUC[ProcessVideo]
        MetricsUC[CalculateMetrics]
        ReportUC[GenerateReport]
    end

    subgraph "Domain Layer (Core)"
        MatchEnt["Match Entity"]
        TrackingEnt["Tracking Data"]
        TacticalEnt["Tactical Metrics"]
    end

    subgraph "Infrastructure Layer (Adapters)"
        DB["PostgreSQL (Repositories)"]
        S3["MinIO (Object Storage)"]
        Celery["Celery Workers"]
        YOLO["YOLOv8 Model"]
    end

    API --> IngestUC
    API --> VideoUC
    API --> MetricsUC
    API --> ReportUC

    IngestUC --> MatchEnt
    VideoUC --> TrackingEnt
    MetricsUC --> TacticalEnt

    IngestUC -.-> DB
    VideoUC -.-> S3
    VideoUC -.-> YOLO
    MetricsUC -.-> DB
```

## 2. Data Ingestion Flow

```mermaid
sequenceDiagram
    participant API as "API (IngestionRouter)"
    participant UC as "IngestionStarter (Use Case)"
    participant Worker as "Celery Worker"
    participant Adapter as StatsBombAdapter
    participant DB as PostgresMatchRepo

    API->>UC: ingest_match(provider, match_id)
    UC->>Worker: dispatch_task("ingest_match", ...)
    Worker->>Adapter: fetch_match_data(match_id)
    Adapter->>Adapter: transform_to_domain(raw_data)
    Adapter-->>Worker: "Match (Rich Entity)"
    Worker->>DB: save(match)
    DB-->>Worker: success
```

## 3. Video Processing Pipeline (GPU)

```mermaid
sequenceDiagram
    participant API as "API (VideoRouter)"
    participant UC as "VideoProcessor (Use Case)"
    participant Worker as "GPU Worker"
    participant Storage as "MinIO (Object Storage)"
    participant YOLO as "YOLOv8 Detector"
    participant Byte as ByteTrack

    API->>UC: process_video(match_id, video_file)
    UC->>Storage: upload_video()
    UC->>Worker: dispatch_task("process_video", ...)

    loop For each frame
        Worker->>Storage: get_frame()
        Worker->>YOLO: detect_objects(frame)
        YOLO-->>Worker: "Detections (Ball, Players)"
        Worker->>Byte: track_objects(detections)
        Byte-->>Worker: Track IDs
    end

    Worker->>Worker: transform_to_parquet()
    Worker->>Storage: save_tracking_data(parquet)
```

## 4. Tactical Metrics Calculation

```mermaid
sequenceDiagram
    participant API as "API (MetricsRouter)"
    participant UC as "MetricsCalculator (Use Case)"
    participant Worker as "Celery Worker"
    participant Repo as MetricsRepository
    participant Entity as "Rich Entities"

    API->>UC: calculate_metrics(match_id)
    UC->>Worker: dispatch_task("calculate_metrics", ...)
    Worker->>Repo: load_tracking_data(match_id)
    Worker->>Repo: load_event_data(match_id)

    loop For each frame
        Worker->>Entity: MatchFrame.calculate_pitch_control()
        Worker->>Entity: PlayerTrajectory.calculate_speed()
        Worker->>Entity: MatchFrame.calculate_pressure()
    end

    Worker->>Repo: save_physical_stats(stats)
    Worker->>Repo: save_tactical_metrics(metrics)
```

## 5. Pattern Detection (Unsupervised ML)

```mermaid
sequenceDiagram
    participant API as "API (PatternsRouter)"
    participant UC as "PatternDetector (Use Case)"
    participant Extractor as SequenceExtractor
    participant ML as SklearnPatternDetector
    participant Labeler as PatternLabeler
    participant Repo as PatternRepository

    API->>UC: detect_patterns(match_id)
    UC->>Extractor: extract_sequences(events)
    Extractor-->>UC: List[PossessionSequence]

    UC->>ML: fit(sequences)
    ML-->>UC: Clusters

    loop For each cluster
        UC->>Labeler: label_pattern(cluster)
        Labeler-->>UC: "Label (e.g. Counter Attack)"
    end

    UC->>Repo: save_patterns(patterns)
```

## 6. Report Generation

```mermaid
sequenceDiagram
    participant API as "API (ReportsRouter)"
    participant UC as "ReportGenerator (Use Case)"
    participant Repo as MetricsRepository
    participant Chart as ChartGenerator
    participant PDF as WeasyPrint
    participant S3 as "Object Storage"

    API->>UC: generate_report(match_id)
    UC->>Repo: fetch_match_summary()
    UC->>Repo: fetch_tactical_stats()

    UC->>Chart: generate_heatmap(tracking_data)
    Chart-->>UC: Image Bytes

    UC->>Chart: generate_pass_network(events)
    Chart-->>UC: Image Bytes

    UC->>PDF: render_html_template(stats, images)
    PDF-->>UC: PDF Bytes

    UC->>S3: save_report(pdf)
    UC-->>API: Report URL
```

## 7. Pitch Calibration

```mermaid
sequenceDiagram
    participant API as "API (CalibrationRouter)"
    participant UC as "VideoCalibrator (Use Case)"
    participant Worker as "Celery Worker"
    participant CV as HomographyEngine
    participant Repo as CalibrationRepository

    API->>UC: start_calibration(video_id, keypoints)
    UC->>Worker: dispatch_task("calibrate_pitch", ...)
    Worker->>CV: compute_homography(keypoints)
    CV-->>Worker: HomographyMatrix

    Worker->>Repo: save_calibration(homography)
    Worker-->>API: Success
```

## 8. Phase Classification

```mermaid
sequenceDiagram
    participant API as "API (PhasesRouter)"
    participant Worker as "Celery Worker"
    participant ML as SklearnPhaseClassifier
    participant Repo as PhaseRepository

    API->>Worker: dispatch_task("classify_match_phases", ...)

    loop For each frame/window
        Worker->>Repo: load_frame_data()
        Worker->>ML: predict_phase(features)
        ML-->>Worker: Phase Label
    end

    Worker->>Repo: save_phases(phases)
```

## 9. Agentic Match Analysis (CrewAI)

```mermaid
sequenceDiagram
    participant API as "API (ChatRouter)"
    participant UC as "MatchAnalyzer (Use Case)"
    participant Worker as "Celery Worker"
    participant Agent as "CrewAI (Analyst Agents)"
    participant RAG as RAGContextBuilder

    API->>UC: analyze_match(match_id, query)
    UC->>Worker: dispatch_task("analyze_match", ...)

    Worker->>RAG: build_match_context(match_id)
    RAG-->>Worker: Context String

    Worker->>Agent: Agent(context).execute(query)
    Agent-->>Worker: Analysis Text

    Worker-->>API: Job Result
```
