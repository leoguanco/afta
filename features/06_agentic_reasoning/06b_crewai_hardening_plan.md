# Implementation Plan - CrewAI Hardening

## Goal Description

Enhance the `CrewAIAdapter` to provide deep, data-driven tactical insights. Currently, the agents might rely on "hallucinated" or generic football knowledge because they lack specific match data in their context. We will implement a mechanism to fetch match metrics (possession, shots, etc.) and inject them into the agent's prompt context.

## User Review Required

> [!IMPORTANT]
> This feature depends on the completion of **Ingestion Persistence (02b)** because we need to query `PostgresMatchRepo` to get the context data.

## Proposed Changes

### Infrastructure Layer

#### [MODIFY] [crewai_adapter.py](file:///d:/Workspace/afta/backend/src/infrastructure/adapters/crewai_adapter.py)

- **Method `run_analysis`**: Update signature to accept `match_context: str` (or a `Dict` of stats).
- **Method `create_tasks`**: Update the `description` string to include this `match_context`.
- **Method `create_agents`**: Enhance `backstory` to explicitly instruct agents to _use_ the provided data points.

#### [MODIFY] [crewai_tasks.py](file:///d:/Workspace/afta/backend/src/infrastructure/worker/tasks/crewai_tasks.py)

- Import `PostgresMatchRepo`.
- In `run_crewai_analysis_task`:
  - Instantiate `repo = PostgresMatchRepo()`.
  - Fetch match data: `match = repo.get_match(match_id)`.
  - **Context Builder**: Create a summary string `context_str` (e.g., "Home Team: X Goals, Away Team: Y Goals...").
  - Pass `context_str` to `adapter.run_analysis`.

## Verification Plan

### Automated Tests

- **Unit Test**: `tests/infrastructure/adapters/test_crewai_adapter.py`
  - Verify `create_tasks` correctly includes the passed `match_context` string in the Task description.

### Manual Verification

- **Query Test**: Ask "Who had more possession?" for a specific match.
- **Success Criteria**: The answer matches the data in `PostgresMatchRepo` and is not a generic "I cannot see the match" response.
