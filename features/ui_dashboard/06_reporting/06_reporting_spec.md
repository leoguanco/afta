# ✨ Feature Specification: Reporting Component

> **Context:** This spec is part of the [UI Dashboard](./ui_dashboard_spec.md) feature. For infrastructure setup, see [dashboard_infrastructure_spec.md](./dashboard_infrastructure_spec.md).

## 1. 🚀 Overview & Motivation

- **Feature Name:** PDF Report Generation
- **Goal:** Allow users to export match analysis as a professional PDF report for sharing with coaching staff.
- **Problem Solved (The "Why"):** Stakeholders (management, coaches) need shareable documents that summarize findings.
- **Scope:**
  - **In Scope:** PDF generation with charts, tables, AI summary, download functionality.
  - **Out of Scope:** Word/Excel export, email integration.

---

## 2. 👥 User Stories & Acceptance Criteria

### **User Story 1:** As a **Coach**, I want to **download a PDF report**, so that **I can share insights with staff.**

| Criteria ID | Acceptance Criteria                                                             | Status |
| :---------- | :------------------------------------------------------------------------------ | :----- |
| US1.1       | The UI SHALL generate a PDF with match summary, graphs, and AI recommendations. | [ ]    |
| US1.2       | The PDF SHALL contain at least 2 graphs and 1 text summary.                     | [ ]    |
| US1.3       | The PDF SHALL be branded with team logo (if uploaded).                          | [ ]    |

### **User Story 2:** As an **Analyst**, I want to **customize the report**, so that **I can include relevant sections.**

| Criteria ID | Acceptance Criteria                                                         | Status |
| :---------- | :-------------------------------------------------------------------------- | :----- |
| US2.1       | The UI SHALL allow toggling sections (Physical Metrics, Tactical Analysis). | [ ]    |

---

## 3. 🏗️ Technical Implementation Plan

### **3.1 Architecture**

- **Component:** `ReportGenerator` (React)
- **Dependencies:**
  - `jspdf` or `react-pdf`: PDF generation
  - `html2canvas`: Chart screenshots
  - `shadcn/ui`: Checkbox components

### **3.2 Report Structure**

1. **Header:** Match info (teams, date, score)
2. **Executive Summary:** AI-generated insights
3. **Physical Metrics:** Distance, speed, sprints (table + chart)
4. **Tactical Analysis:** PPDA, Pitch Control (heatmap screenshot)
5. **Recommendations:** AI suggestions

### **3.3 Implementation Steps**

1. **Template Design:** Create PDF layout with sections.
2. **Chart Export:** Convert Recharts to static images.
3. **PDF Assembly:** Combine text and images with jspdf.
4. **Download:** Trigger browser download.

---

## 4. 🔒 Constraints & Edge Cases

- **Constraints:**
  - PDF size: Maximum 10MB.
  - Format: A4 portrait.
- **Edge Cases:**
  - **Missing AI Summary:** Use fallback template text.
  - **Chart Render Failure:** Show placeholder image.

---

## 5. 🧪 Testing & Validation Plan

- **Test Scenarios:**
  - **Scenario 1:** Click "Generate Report" → PDF downloads with 2+ graphs.
  - **Scenario 2:** Uncheck "Physical Metrics" → PDF excludes that section.
