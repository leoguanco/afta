# Ingestion Persistence Implementation Plan

## Goal Description

Implement database persistence for the Data Ingestion module. This involves creating a PostgreSQL repository adapter to save normalized `Match` and `Event` entities, ensuring that data fetched from providers (StatsBomb, Metrica) is permanently stored and queryable.

## User Review Required

> [!IMPORTANT]
> This change introduces a hard dependency on the PostgreSQL database for the Ingestion Worker. Ensure the `postgres` service is running and migrations are applied before deployment.

## Proposed Changes

### Infrastructure Layer

#### [NEW] [postgres_match_repo.py](file:///d:/Workspace/afta/backend/src/infrastructure/db/repositories/postgres_match_repo.py)

- Implement `PostgresMatchRepo` class inheriting from `MatchRepository`.
- Implement `save(match: Match)` method using SQLAlchemy session.
- Map Domain Entities (`Match`, `Event`) to SQLAlchemy Models (`MatchModel`, `EventModel`).

#### [MODIFY] [ingestion_tasks.py](file:///d:/Workspace/afta/backend/src/infrastructure/worker/tasks/ingestion_tasks.py)

- Import `PostgresMatchRepo`.
- Instantiate repository in `ingest_match_task`.
- Replace `TODO` with `repo.save(match)`.

## Verification Plan

### Automated Tests

- **Integration Test:** `tests/integration/test_ingestion_persistence.py`
  - Start a test transaction.
  - Create a dummy `Match` entity with events.
  - Call `repo.save(match)`.
  - Query the database to verify logical existence of rows.
  - Rollback transaction.

### Manual Verification

- Run an ingestion job via API: `POST /api/v1/ingest`.
- Check Celery logs for "Ingestion complete".
- Connect to DB (`docker exec -it afta-db psql ...`) and run `SELECT * FROM matches;`.
