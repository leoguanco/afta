# ✨ Feature Specification: CrewAI Integration Hardening

## 1. 🚀 Overview & Motivation

- **Feature Name:** CrewAI Production Hardening
- **Goal:** Transform the basic `CrewAI` implementation into a production-ready feature with rich context and robust prompting.
- **Problem Solved (The "Why"):** The current implementation exists but lacks the depth of context required for high-quality tactical analysis (e.g., passing actual match metrics).
- **Scope:**
  - **In Scope:** `CrewAIAdapter` logic enhancement, Context Injection mechanism.
  - **Out of Scope:** New Agents.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As an **Analyst**, I want **answers based on data**, not generalities.

| Criteria ID | Acceptance Criteria                                                                                        | Status |
| :---------- | :--------------------------------------------------------------------------------------------------------- | :----- |
| US1.1       | The system SHALL inject a summary of match statistics (goals, shots, possession) into the Agent's context. | [ ]    |
| US1.2       | The Analyst Agent SHALL cite specific data points in its response.                                         | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture and Dependencies**

- **Affected Components:**
  - `src/infrastructure/adapters/crewai_adapter.py`
  - `src/infrastructure/worker/tasks/crewai_tasks.py`

### **3.2 Implementation Steps**

1.  **Context Builder:**
    - Create a helper method `build_match_context(match_id)` that fetches data from `PostgresMatchRepo` (once fixed).
    - Format this data as a markdown string.
2.  **Agent Config:**
    - Update `backstory` to emphasize "data-driven" analysis.
3.  **Task Execution:**
    - Pass this context string into the `Task` description.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - **Context Window:** Summarize data to fit within token limits.

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** Manual query testing.
