# Agentic Reasoning Implementation Plan

This plan details the implementation of the `Agentic Reasoning` feature as specified in `agentic_reasoning_spec.md`. The goal is to connect Domain Logic to AI providers via an asynchronous interface to handle slow LLM response times.

## User Review Required

> [!IMPORTANT] > **Async Architecture**: This feature introduces a pattern where API responses are immediate (returning a `job_id`), while the actual heavy lifting happens in specific Celery workers. The UI will need to poll for status.

## Proposed Changes

### Domain Layer

#### [NEW] [analysis_port.py](../../backend/src/domain/ports/analysis_port.py)

- Define `AnalysisPort` interface.
- **Methods**: `analyze_match(match_id: str, query: str) -> str` (returns job_id).

#### [NEW] [analysis_job.py](../../backend/src/domain/entities/analysis_job.py)

- **Rich Entity**: `AnalysisJob`.
- **Fields**: `job_id`, `status` (PENDING, RUNNING, COMPLETED, FAILED), `result`, `error`.
- **Methods**: State transitions logic.

### Infrastructure Layer

#### [NEW] [crewai_adapter.py](../../backend/src/infrastructure/adapters/crewai_adapter.py)

- Implement `AnalysisPort`.
- **Responsibility**: Dispatch Celery tasks.

#### [NEW] [crewai_tasks.py](../../backend/src/infrastructure/worker/tasks/crewai_tasks.py)

- **Celery Task**: `run_crewai_analysis_task`.
- **Queue**: `general` (CPU-bound, no GPU required).
- **Logic**: Initialize CrewAI agents, run analysis, update job status/result in DB/Redis.
- **Observability**: Record `llm_request_duration_seconds` and `llm_tokens_total` metrics.

#### [NEW] [chat.py](../../backend/src/infrastructure/api/endpoints/chat.py)

- **API Endpoint**: `POST /api/v1/chat/analyze`.
- **Logic**: Use `AnalysisPort` to start job.
- **API Endpoint**: `GET /api/v1/chat/jobs/{job_id}`.
- **Logic**: Retrieve job status.

## Verification Plan

### Automated Tests

- **Unit Test**: `test_analysis_job.py`
  - Verify `AnalysisJob` state transitions (e.g., cannot go from FAILED to PENDING).
  - Ensure TDD best practices.
- **Integration Test**: `test_agentic_reasoning_flow.py`
  - Mock `CrewAI` (avoid expensive/slow calls).
  - Test Flow:
    1.  Call `dispatch` -> Get ID.
    2.  Simulate Worker execution (update state).
    3.  Check Status -> Expect `COMPLETED`.

```bash
pytest backend/tests/integration/test_agentic_reasoning_flow.py
```

### Manual Verification

1.  **Trigger API**: Use Swagger UI or `curl` to POST a question.
2.  **Monitor Logs**: Check Celery worker logs for "Agent starting...".
3.  **Poll Status**: Check the status endpoint until completed.
