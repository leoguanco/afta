# ✨ Feature Specification: Tactical Report Generation

> **Context:** This spec is part of the [Football Intelligence Engine](../feature_specs.md) project. For infrastructure constraints (TDD, Hexagonal Architecture, Async Workers), see [../01_infrastructure/01_infrastructure_spec.md](../01_infrastructure/01_infrastructure_spec.md).

## 1. 🚀 Overview & Motivation

- **Feature Name:** Tactical Report Generation (Export Engine)
- **Goal:** Generate comprehensive tactical reports in multiple formats (JSON, PDF) combining metrics, visualizations, and LLM-generated narrative analysis.
- **Problem Solved (The "Why"):** Analysts need to share insights with coaches and staff who may not have access to the dashboard. A formatted PDF report with visualizations provides a portable, professional deliverable. The current system calculates metrics but has no export capability.
- **Scope:**
  - **In Scope:** JSON export, PDF generation with charts, LLM narrative sections, template system.
  - **Out of Scope:** Real-time streaming reports, video embedding in PDF.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Tactical Analyst**, I want **to export a match report as PDF**, so that **I can share it with coaching staff.**

| Criteria ID | Acceptance Criteria                                                                 | Status |
| :---------- | :---------------------------------------------------------------------------------- | :----- |
| US1.1       | The system SHALL generate a PDF report with match summary, key metrics, and charts. | [x]    |
| US1.2       | The report SHALL include pitch visualizations (heatmaps, pass networks).            | [x]    |
| US1.3       | The report SHALL be generated asynchronously and downloadable via API.              | [x]    |

### **User Story 2:** As a **Developer**, I want **structured JSON export**, so that **I can integrate with other tools.**

| Criteria ID | Acceptance Criteria                                                | Status |
| :---------- | :----------------------------------------------------------------- | :----- |
| US2.1       | The system SHALL export all calculated metrics as structured JSON. | [x]    |
| US2.2       | The JSON schema SHALL be documented and versioned.                 | [x]    |

### **User Story 3:** As an **Analyst**, I want **LLM narrative in the report**, so that **key insights are explained in natural language.**

| Criteria ID | Acceptance Criteria                                                        | Status |
| :---------- | :------------------------------------------------------------------------- | :----- |
| US3.1       | The PDF SHALL include an "AI Analysis" section with LLM-generated content. | [x]    |
| US3.2       | The narrative SHALL reference specific metrics and events from the match.  | [x]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture (Hexagonal + Async)**

- **Domain Layer:**
  - `src/domain/entities/tactical_report.py`: Rich entity containing report structure
  - `src/domain/value_objects/report_section.py`: Value object for report sections
  - `src/domain/ports/report_generator_port.py`: Interface for report generation
- **Infrastructure Layer:**
  - `src/infrastructure/reports/pdf_generator.py`: WeasyPrint/ReportLab implementation
  - `src/infrastructure/reports/chart_generator.py`: Matplotlib/mplsoccer visualizations
  - `src/infrastructure/reports/json_exporter.py`: Structured JSON export
  - `src/infrastructure/worker/tasks/report_tasks.py`: Async report generation
- **Application Layer:**
  - `src/application/use_cases/generate_tactical_report.py`: Orchestrates report creation

### **3.2 Implementation Steps**

1.  **Define Domain:** Create `TacticalReport` entity with sections (Summary, Metrics, Visualizations, Analysis).
2.  **JSON Export:** Implement structured export with versioned schema.
3.  **Chart Generation:** Create pitch visualizations using mplsoccer.
4.  **PDF Template:** Design HTML/CSS template for professional report layout.
5.  **LLM Integration:** Call existing CrewAI adapter to generate narrative sections.
6.  **Async Task:** Create Celery task for full report generation pipeline.
7.  **API Endpoint:** Add `/api/v1/reports/generate` and `/api/v1/reports/{id}/download`.

---

## 4. 🔒 Constraints, Assumptions, & Edge Cases

- **Constraints:**
  - PDF generation should complete in <30 seconds for a single match.
  - PDF file size should be <10MB.
  - Must work without external font dependencies (use web-safe fonts).
- **Assumptions:**
  - All metrics are pre-calculated before report generation.
  - LLM is available and responsive (with timeout fallback).
- **Edge Cases:**
  - **LLM timeout:** Generate report without AI section, mark as "Analysis pending".
  - **Missing metrics:** Include "Data not available" for missing sections.
  - **Large match:** Paginate visualizations if needed.

---

## 5. 🧪 Testing & Validation Plan

- **Test Strategy:** TDD with unit tests for each generator, integration test for full pipeline.
- **Key Test Scenarios:**
  - **Scenario 1:** Generate JSON export → validate against schema.
  - **Scenario 2:** Generate PDF → verify file is valid PDF with expected page count.
  - **Scenario 3:** Generate report with mock LLM → verify narrative section present.

---

## 6. 🔗 References and Related Documentation

- [mplsoccer Documentation](https://mplsoccer.readthedocs.io/)
- [WeasyPrint](https://weasyprint.org/)
- [Football Analytics Report Examples](https://statsbomb.com/articles/)
