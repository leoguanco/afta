# ✨ Feature Specification: CrewAI Integration (Real Implementation)

## 1. 🚀 Overview & Motivation

- **Feature Name:** CrewAI Production Integration
- **Goal:** Replace the current mock Agentic implementation with a real CrewAI integration that uses LLMs (OpenAI/Anthropic) to analyze matches.
- **Problem Solved (The "Why"):** The current `_run_mock_analysis` provides static responses. We need dynamic, context-aware analysis to provide actual value to coaches.
- **Scope:**
  - **In Scope:** `CrewAIAdapter`, `AnalysisAgent`, `ResearchAgent`, `ReportAgent` configuration, Integration with `AnalysisJob` entity.
  - **Out of Scope:** Local LLM hosting (we will use API calls).

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As an **Analyst**, I want **real AI insights**, so that **I can find patterns I missed.**

| Criteria ID | Acceptance Criteria | Status                                                                                   |
| :---------- | :------------------ | :--------------------------------------------------------------------------------------- | --- |
| 20:         | US1.1               | The system SHALL instantiate a CrewAI crew with at least 2 agents (Analyst, Writer).     | [x] |
| 21:         | US1.2               | The system SHALL pass the user's query and match context (metadata/stats) to the agents. | [x] |
| 22:         | US1.3               | The system SHALL return the final text output from the CrewAI execution.                 | [x] |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture and Dependencies**

- **Affected Components:**
  - `src/infrastructure/worker/tasks/crewai_tasks.py` (Replace mock)
  - `src/infrastructure/adapters/crewai_adapter.py`
- **New Dependencies:**
  - `crewai`: For agent orchestration.
  - `langchain_openai`: For LLM connection.
- **Data Model Changes:** None.

### **3.2 Implementation Steps (High-Level)**

1.  **Configure Agents:** Create `agent_config.yaml` and `task_config.yaml` defining agent personas and tasks.
2.  **Make Dependencies:** Use `Container` (DI) to resolve `CrewAIAdapter` and Repositories.
3.  **Context Injection:** Fetch match summaries (from `PostgresMatchRepo` or similar) to inject as context.
4.  **Execute:**
    - **Sync:** Run `crew.kickoff()` for background tasks.
    - **Stream:** Use `anyio` thread pool to stream events via SSE for real-time feedback.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - **Cost Control:** Must use `gpt-4o-mini` or `gpt-3.5-turbo` for routine queries to save costs.
  - **Timeout:** CrewAI execution must not exceed 120 seconds.
- **Edge Cases:**
  - **LLM Rate Limit:** Handle `RateLimitError` with a friendly error message and retry.

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** VCR/Betamax for recording LLM responses in integration tests.
- **Key Test Scenarios:**
  - **Scenario 1:** Run analysis with a "Why did we lose?" query -> Verify response contains tactical keywords.
