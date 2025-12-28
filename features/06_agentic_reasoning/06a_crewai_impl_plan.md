# CrewAI Integration Implementation Plan

## Goal Description

Implement the Agentic Reasoning feature using CrewAI, replacing the current mock implementation. This involves creating a `CrewAIAdapter` that orchestrates a multi-agent system (Analysts, Writers) to process natural language queries about match data, providing deeper, context-aware insights.

## User Review Required

> [!WARNING]
> This feature requires valid API keys for LLM providers (e.g., `OPENAI_API_KEY`) to be set in the environment variables.

## Proposed Changes

### Infrastructure Layer

#### [NEW] [crewai_adapter.py](../../../backend/src/infrastructure/adapters/crewai_adapter.py)

- Implement `CrewAIAdapter` class implementing `AnalysisPort`.
- Define CrewAI `Agent` objects:
  - **Analyst:** Specialized in tactical football analysis.
  - **Writer:** Specialized in summarizing findings into a coherent report.
- Define `Task` objects linked to the agents.
- Implement `dispatch_analysis(job: AnalysisJob)` to:
  - Instantiate the Crew.
  - Run `crew.kickoff(inputs={...})` synchronously (wrapped in async task).
  - Return the result.

#### [MODIFY] [crewai_tasks.py](../../../backend/src/infrastructure/worker/tasks/crewai_tasks.py)

- Import `CrewAIAdapter`.
- Replace `_run_mock_analysis` with `adapter.dispatch_analysis`.
- Ensure appropriate error handling for LLM timeouts/failures.

## Verification Plan

### Automated Tests

- **Integration Test (Mocked):** `tests/integration/test_crewai_flow.py`
  - Utilize VCR.py or a similar library to record/mock the HTTP interactions with the OpenAI API during testing to avoid costs and ensure determinism.
  - assert that the adapter returns a string response when the mock "LLM" returns success.

### Manual Verification

- Start the worker with `OPENAI_API_KEY` configured.
- Send a chat request via `POST /api/v1/chat/analyze`.
- Question: "Analyze high press efficiency".
- Poll status until "COMPLETED".
- Verify the response contains coherent text rather than the hardcoded mock string.
