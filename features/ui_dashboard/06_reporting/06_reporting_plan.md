# Implementation Plan: Reporting Component

> **Reference Spec:** [06_reporting_spec.md](./06_reporting_spec.md)

## Overview

PDF report generation with charts, statistics, and AI-generated summaries for sharing with coaching staff.

---

## Design Reference

Based on mockups:

- **Preview:** Modal showing report sections
- **Controls:** Toggle checkboxes for sections
- **Output:** A4 portrait PDF with branding

---

## Component Structure

```
components/reporting/
├── ReportGenerator.tsx    # Main modal/panel
├── ReportPreview.tsx      # Preview before export
├── SectionToggle.tsx      # Checkbox for each section
├── ReportHeader.tsx       # Match info header
└── hooks/
    └── usePdfExport.ts    # PDF generation logic
```

---

## Implementation Steps

### 1. ReportGenerator Modal

```tsx
interface ReportGeneratorProps {
  matchId: string;
  isOpen: boolean;
  onClose: () => void;
}

const SECTIONS = [
  { id: "summary", label: "Executive Summary", default: true },
  { id: "physical", label: "Physical Metrics", default: true },
  { id: "tactical", label: "Tactical Analysis", default: true },
  { id: "phases", label: "Phase Breakdown", default: true },
  { id: "recommendations", label: "AI Recommendations", default: true },
];

export function ReportGenerator({ matchId, isOpen, onClose }: Props) {
  const [selectedSections, setSelectedSections] = useState(
    SECTIONS.filter((s) => s.default).map((s) => s.id)
  );
  const { generatePdf, isGenerating } = usePdfExport();

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Generate Report</DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-4">
          <SectionToggles
            sections={SECTIONS}
            selected={selectedSections}
            onChange={setSelectedSections}
          />
          <ReportPreview matchId={matchId} sections={selectedSections} />
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={() => generatePdf(matchId, selectedSections)}
            disabled={isGenerating}
          >
            {isGenerating ? "Generating..." : "Download PDF"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

### 2. Section Toggles

```tsx
<div className="space-y-2">
  {sections.map((section) => (
    <label key={section.id} className="flex items-center gap-2">
      <Checkbox
        checked={selected.includes(section.id)}
        onCheckedChange={(checked) => {
          if (checked) {
            onChange([...selected, section.id]);
          } else {
            onChange(selected.filter((id) => id !== section.id));
          }
        }}
      />
      <span>{section.label}</span>
    </label>
  ))}
</div>
```

### 3. Report Preview

```tsx
export function ReportPreview({ matchId, sections }: Props) {
  const { data: match } = useMatch(matchId);
  const { data: metrics } = useMatchMetrics(matchId);

  return (
    <div className="bg-white text-black p-4 rounded shadow max-h-96 overflow-auto">
      {/* Header */}
      <div className="text-center border-b pb-4 mb-4">
        <h1 className="text-xl font-bold">Match Report</h1>
        <p>
          {match?.home_team_id} vs {match?.away_team_id}
        </p>
      </div>

      {/* Sections preview */}
      {sections.includes("summary") && (
        <section className="mb-4">
          <h2 className="font-semibold">Executive Summary</h2>
          <p className="text-sm text-gray-600">AI-generated overview...</p>
        </section>
      )}

      {sections.includes("physical") && (
        <section className="mb-4">
          <h2 className="font-semibold">Physical Metrics</h2>
          <div className="h-32 bg-gray-100 rounded flex items-center justify-center">
            [Distance/Speed Chart]
          </div>
        </section>
      )}

      {/* ... other sections */}
    </div>
  );
}
```

### 4. PDF Export Hook

```tsx
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

export function usePdfExport() {
  const [isGenerating, setIsGenerating] = useState(false);

  const generatePdf = async (matchId: string, sections: string[]) => {
    setIsGenerating(true);

    try {
      const pdf = new jsPDF("p", "mm", "a4");
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      let yOffset = 20;

      // Title
      pdf.setFontSize(20);
      pdf.text("Match Analysis Report", pageWidth / 2, yOffset, {
        align: "center",
      });
      yOffset += 20;

      // Capture charts as images
      for (const sectionId of sections) {
        const element = document.getElementById(`report-section-${sectionId}`);
        if (element) {
          const canvas = await html2canvas(element);
          const imgData = canvas.toDataURL("image/png");

          const imgWidth = pageWidth - 40;
          const imgHeight = (canvas.height * imgWidth) / canvas.width;

          // Check if we need a new page
          if (yOffset + imgHeight > pageHeight - 20) {
            pdf.addPage();
            yOffset = 20;
          }

          pdf.addImage(imgData, "PNG", 20, yOffset, imgWidth, imgHeight);
          yOffset += imgHeight + 10;
        }
      }

      // Download
      pdf.save(`match-report-${matchId}.pdf`);
    } finally {
      setIsGenerating(false);
    }
  };

  return { generatePdf, isGenerating };
}
```

---

## Report Structure

1. **Header**

   - Team logos (if available)
   - Match date and competition
   - Final score

2. **Executive Summary**

   - AI-generated 2-3 paragraph overview
   - Key highlights

3. **Physical Metrics** (Table + Chart)

   - Total distance per player
   - Sprint count
   - High-intensity runs

4. **Tactical Analysis** (Charts)

   - PPDA trend
   - Pitch control heatmap screenshot
   - Formation diagram

5. **Phase Breakdown**

   - Pie chart of phase percentages
   - Transition count

6. **Recommendations**
   - AI-generated improvement suggestions

---

## Verification

- [ ] Section toggles work correctly
- [ ] Preview updates when toggling
- [ ] PDF generates without errors
- [ ] Charts render in PDF
- [ ] PDF downloads with correct filename
- [ ] File size < 10MB
