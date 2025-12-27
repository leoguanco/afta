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

| File                                 | Purpose                                                                                           |
| :----------------------------------- | :------------------------------------------------------------------------------------------------ |
| [NEW] `value_objects/coordinates.py` | Immutable `Coordinates` dataclass with `.from_statsbomb()` and `.from_metrica()` factory methods. |
| [NEW] `entities/event.py`            | `Event` dataclass (type, timestamp, coordinates, player_id).                                      |
| [NEW] `entities/match.py`            | `Match` aggregate root (match_id, home_team, away_team, events: List[Event]).                     |
| [NEW] `ports/match_repository.py`    | Abstract `MatchRepository` interface (get_match, save_match).                                     |

---

### Infrastructure Layer (`backend/src/infrastructure/`)

| File                                    | Purpose                                                                                  |
| :-------------------------------------- | :--------------------------------------------------------------------------------------- |
| [NEW] `adapters/statsbomb_adapter.py`   | Implements `MatchRepository` using `statsbombpy`. Maps external data to Domain entities. |
| [NEW] `adapters/metrica_adapter.py`     | Implements `MatchRepository` using `pandas` to parse CSVs.                               |
| [NEW] `worker/tasks/ingestion_tasks.py` | Celery task routed to `default_queue` (CPU worker).                                      |
| [NEW] `logging/json_logger.py`          | Central logger emitting **JSON only on errors** with `trace_id`.                         |

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
# 1. Run Domain Unit Tests (Pure Logic)
docker-compose exec api pytest tests/domain/ -v

# 2. Run Infrastructure Integration Tests (StatsBomb)
docker-compose exec api pytest tests/infrastructure/ -v

# 3. Run Full Suite
docker-compose exec api pytest --cov=src --cov-report=term-missing
```

### Manual Verification

1.  `POST /api/v1/ingest` with `{"source": "statsbomb", "match_id": "3869519"}`.
2.  Verify `job_id` is returned.
3.  Check Flower ([http://localhost:5555](http://localhost:5555)) for task in `default` queue.
4.  Trigger a deliberate error and verify JSON log output in container stdout.
