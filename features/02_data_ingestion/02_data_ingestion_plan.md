# Implementation Plan: Data Ingestion Feature

## Goal

Implement the **Data Ingestion** module as defined in [data_ingestion_spec.md](../specs/data_ingestion_spec.md), strictly adhering to the [infrastructure_spec.md](../specs/infrastructure_spec.md) constraints.

---

## User Review Required

> [!IMPORTANT] > **TDD Mandatory:** Every new file below will have its corresponding test written **FIRST** (Red-Green-Refactor).

> [!WARNING] > **Domain Purity:** The `domain/` layer files will **NOT** import `pandas`, `sqlalchemy`, `fastapi`, or any external library. Only Python stdlib and `dataclasses`.

---

## Proposed Changes

### Domain Layer (`backend/src/domain/`)

| File                                 | Purpose                                                                                                                                                                            |
| :----------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [NEW] `value_objects/coordinates.py` | Immutable `Coordinates` dataclass with factory methods implementing **Linear Scaling**: <br> - StatsBomb (0-120, 0-80) -> (0-105, 0-68) <br> - Metrica (0-1, 0-1) -> (0-105, 0-68) |
| [NEW] `entities/event.py`            | `Event` dataclass with strictly typed `EventType` Enum (Pass, Shot, Carry).                                                                                                        |
| [NEW] `entities/match.py`            | `Match` aggregate root (match_id, home_team, away_team, events: List[Event]).                                                                                                      |
| [NEW] `ports/match_repository.py`    | Abstract `MatchRepository` interface (get_from_source, save).                                                                                                                      |

---

### Infrastructure Layer (`backend/src/infrastructure/`)

#### Adapters (External Data)

| File                                  | Purpose                                                                           |
| :------------------------------------ | :-------------------------------------------------------------------------------- |
| [NEW] `adapters/statsbomb_adapter.py` | Implements `MatchRepository` using `statsbombpy`. Normalizes 120x80 coords.       |
| [NEW] `adapters/metrica_adapter.py`   | Implements `MatchRepository` using `pandas` to parse CSVs. Normalizes 0-1 coords. |

#### Storage (Database)

| File                                           | Purpose                                                                                      |
| :--------------------------------------------- | :------------------------------------------------------------------------------------------- |
| [NEW] `db/models.py`                           | SQLAlchemy Models definitions: `MatchModel`, `EventModel` (mapping to `match_events` table). |
| [NEW] `db/repositories/postgres_match_repo.py` | Adapter to persist Domain Entities to PostgreSQL.                                            |

#### Context & Workers

| File                                    | Purpose                                                                                                                           |
| :-------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| [NEW] `worker/tasks/ingestion_tasks.py` | Celery task (`@celery.task(queue='default')`) that orchestrates: <br> 1. Fetch from Adapter <br> 2. Normalize <br> 3. Save to DB. |
| [NEW] `logging/json_logger.py`          | Central logger emitting **JSON only on errors** with `trace_id`.                                                                  |

---

### Application Layer (`backend/src/application/`)

| File                                 | Purpose                                                                    |
| :----------------------------------- | :------------------------------------------------------------------------- |
| [NEW] `use_cases/start_ingestion.py` | Orchestrator that creates a Job, dispatches Celery task, returns `job_id`. |

---

## Constraints Checklist (from infrastructure_spec.md)

| Constraint             | How We Enforce It                                                                                 |
| :--------------------- | :------------------------------------------------------------------------------------------------ |
| **TDD**                | Test files created _before_ implementation (e.g., `test_coordinates.py` before `coordinates.py`). |
| **Hexagonal Purity**   | `domain/` imports only `dataclasses`, `enum`, `abc`. No external libs.                            |
| **JSON Error Logging** | `json_logger.py` uses `structlog` configured for JSON output on `ERROR` level only.               |
| **Celery Routing**     | Ingestion tasks use `@celery.task(queue='default')` to target the CPU worker.                     |
| **Prometheus Metrics** | Add `ingestion_jobs_total` counter via `prometheus-client`.                                       |

---

## Verification Plan

### TDD Commands

```bash
# 1. Run Domain Unit Tests (Pure Logic: Scaling, Enums)
docker-compose exec api pytest tests/domain/ -v

# 2. Run Infrastructure Integration Tests (StatsBomb & DB)
docker-compose exec api pytest tests/infrastructure/ -v

# 3. Run Full Suite
docker-compose exec api pytest --cov=src --cov-report=term-missing
```

### Manual Verification

1.  `POST /api/v1/ingest` with `{"source": "statsbomb", "match_id": "3869519"}`.
2.  Verify `job_id` is returned.
3.  Check Flower ([http://localhost:5555](http://localhost:5555)) for task in `default` queue.
4.  **Database Check:** Connect to DB (`docker-compose exec db psql -U postgres -d afta`) and run:
    ```sql
    SELECT count(*) FROM match_events WHERE match_id = '3869519';
    ```
