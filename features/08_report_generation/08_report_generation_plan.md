# Report Generation Implementation Plan

This plan details the implementation of the Tactical Report Generation feature as specified in `08_report_generation_spec.md`. The goal is to generate exportable PDF and JSON reports with visualizations and LLM narrative.

## User Review Required

> [!IMPORTANT] > **PDF Library Choice**: Using `weasyprint` for PDF generation. Requires system dependencies (`libpango`, `libcairo`). Alternative: `reportlab` for pure Python.

> [!WARNING] > **mplsoccer Dependency**: Adds ~50MB to worker image due to matplotlib.

## Implementation Status

- [ ] Domain Layer (entities, value objects, ports)
- [ ] Chart Generation (mplsoccer)
- [ ] PDF Generation (weasyprint)
- [ ] JSON Export
- [ ] Application Layer (use case)
- [ ] API Endpoints
- [ ] Tests

## Proposed Changes

### Domain Layer

#### [NEW] [report_section.py](../../backend/src/domain/value_objects/report_section.py)

- Implement `ReportSection` value object.
- **Fields**: `title`, `content_type`, `content`, `order`.

#### [NEW] [tactical_report.py](../../backend/src/domain/entities/tactical_report.py)

- Implement `TacticalReport` Rich Entity.
- **Methods**: `add_section()`, `get_sections_by_type()`, `to_json()`.

#### [NEW] [report_generator_port.py](../../backend/src/domain/ports/report_generator_port.py)

- Define `ReportGeneratorPort` interface.
- **Methods**: `generate_pdf()`, `generate_json()`.

---

### Infrastructure Layer

#### [NEW] [chart_generator.py](../../backend/src/infrastructure/reports/chart_generator.py)

- Implement chart generation using `mplsoccer`.
- **Methods**: `generate_pass_network()`, `generate_heatmap()`, `generate_pitch_control_frame()`.

#### [NEW] [pdf_generator.py](../../backend/src/infrastructure/reports/pdf_generator.py)

- Implement `WeasyPrintReportGenerator` adapter.
- **Template**: HTML/CSS with embedded charts.

#### [NEW] [json_exporter.py](../../backend/src/infrastructure/reports/json_exporter.py)

- Implement structured JSON export.
- **Schema**: Versioned (`v1.0`).

#### [NEW] [tactical_report.html](../../backend/src/infrastructure/reports/templates/tactical_report.html)

- HTML template for PDF generation.
- **Sections**: Header, Summary, Metrics, Visualizations, AI Analysis.

#### [NEW] [report_tasks.py](../../backend/src/infrastructure/worker/tasks/report_tasks.py)

- Implement Celery task `generate_report_task`.
- **Flow**: Fetch metrics → Generate charts → Get LLM analysis → Build PDF → Store in MinIO.

---

### Application Layer

#### [NEW] [generate_tactical_report.py](../../backend/src/application/use_cases/generate_tactical_report.py)

- Implement `GenerateTacticalReportUseCase`.
- **Dependencies**: `MetricsRepository`, `AnalysisPort`, `ChartGenerator`, `ReportGeneratorPort`.

---

### API Endpoints

#### [NEW] [reports.py](../../backend/src/infrastructure/api/endpoints/reports.py)

- Add router for report endpoints.
- `POST /api/v1/reports/generate` - Start report generation.
- `GET /api/v1/reports/{id}/download` - Download generated report.

---

## Verification Plan

### Automated Tests

```bash
# Run tests
pytest backend/tests/domain/entities/test_tactical_report.py
pytest backend/tests/infrastructure/reports/test_chart_generator.py
pytest backend/tests/infrastructure/reports/test_pdf_generator.py
```

### Manual Verification

1. **Generate JSON report** via API → Validate against schema.
2. **Generate PDF report** → Open and verify layout.
3. **Check file size** < 10MB.
4. **Verify LLM section** present in PDF.

---

## New Dependencies

```
mplsoccer>=1.2.0
weasyprint>=60.0
```

---

## New Test Files

- `tests/domain/entities/test_tactical_report.py`
- `tests/infrastructure/reports/test_chart_generator.py`
- `tests/infrastructure/reports/test_pdf_generator.py`
- `tests/infrastructure/reports/test_json_exporter.py`
