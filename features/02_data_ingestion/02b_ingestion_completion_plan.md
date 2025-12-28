# Implementation Plan - Ingestion Persistence Completion

## Goal Description

Complete the implementation of `PostgresMatchRepo` to correctly persist and reconstruct `Match` and `Event` entities, replacing existing `TODO` placeholders. This ensures that data ingested from providers like StatsBomb is actually saved to the database and can be retrieved for analysis.

## User Review Required

> [!IMPORTANT]
> This change modifies the core `MatchRepository` implementation. Any existing tests relying on the mocked/incomplete behavior will need to be updated.

## Proposed Changes

### Infrastructure Layer

#### [MODIFY] [postgres_match_repo.py](file:///d:/Workspace/afta/backend/src/infrastructure/db/repositories/postgres_match_repo.py)

- **Method `get_match`**:
  - Remove `events=[] # TODO`.
  - Implement logic to convert `MatchModel.events` (ORM objects) back into a list of `Event` domain entities.
  - Ensure `Coordinates` value object is correctly instantiated from `x` and `y`.
  - Ensure `EventType` enum conversion is safe.
- **Method `save`**:
  - Improve `source` handling: `match.metadata.get("source", "statsbomb")` instead of hardcoded string.
  - Ensure `EventModel` creation iterates over `match.events` correctly. (This part looked mostly done but needs verification).

### Domain Layer

- Verify `Event` entity has all necessary attributes exposed to match the `EventModel` fields.

## Verification Plan

### Automated Tests

- **Integration Test**: `tests/infrastructure/db/test_postgres_match_repo.py`
  - Create a test `test_save_and_retrieve_match_with_events`.
  - Steps:
    1. Create a `Match` with 5 `Event` objects.
    2. `repo.save(match)`.
    3. `retrieved = repo.get_match(match.match_id)`.
    4. Assert `len(retrieved.events) == 5`.
    5. Assert `retrieved.events[0].coordinates.x` matches original.

### Manual Verification

- None required if integration tests pass.
