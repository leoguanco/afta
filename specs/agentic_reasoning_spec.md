# ✨ Feature Specification: Agentic Reasoning (Async Interface)

## 1. 🚀 Overview & Motivation

- **Feature Name:** LLM Infrastructure Adapter (Async)
- **Goal:** Connect Domain Logic to AI providers via an asynchronous interface to handle slow LLM response times.
- **Problem Solved (The "Why"):** LLM calls (especially multi-agent reasoning with CrewAI) can take 30+ seconds. This must be handled asynchronously with a job/status pattern to provide a good user experience in the UI.
- **Scope:**
  - **In Scope:** `AnalysisPort`, `AsyncCrewAIAdapter`, RAG Retrieval, Job Status API.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **User**, I want **to see a "Processing..." indicator in the chat**, so that **I know the AI is thinking.**

| Criteria ID | Acceptance Criteria                                                                  | Status |
| :---------- | :----------------------------------------------------------------------------------- | :----- |
| US1.1       | The UI SHALL poll for the status of an LLM request started via the API.              | [ ]    |
| US1.2       | The background task SHALL update the `Status` and eventual `Result` in the database. | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture (Hexagonal + Async)**

- **Domain:** `AnalysisPort` (Interface).
- **Infrastructure:**
  - `src/infrastructure/agents/crewai_tasks.py`: Background worker calling the LLM.
  - `src/infrastructure/api/endpoints/chat.py`: Initiates the async job.

### **3.2 Implementation Steps**

1.  **Define Port:** `AnalysisService`.
2.  **Async Orchestration:** Use Celery to run the `CrewAI` pipeline.
3.  **Real-time Updates:** Optionally use WebSockets or just Long Polling for status updates.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - Timeouts must be configured for LLM providers (e.g., 60s max).

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** Integration via VCR/Mocking.
- **Key Test Scenarios:**
  - **Scenario 1:** Start a chat job -> Verify status transitions from `PENDING` to `SUCCESS`.

---

## 6. 🔗 References and Related Documentation

- [CrewAI](https://docs.crewai.com/)
