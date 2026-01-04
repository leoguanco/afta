"use client";

import { useState } from "react";
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Skeleton,
} from "@/components/ui";
import { Download, FileText, CheckSquare, Square, Loader2 } from "lucide-react";
import { cn } from "@/src/utils";

interface ReportGeneratorProps {
  matchId: string;
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

interface Section {
  id: string;
  label: string;
  description: string;
  default: boolean;
}

const SECTIONS: Section[] = [
  {
    id: "summary",
    label: "Executive Summary",
    description: "AI-generated match overview",
    default: true,
  },
  {
    id: "physical",
    label: "Physical Metrics",
    description: "Distance, speed, sprints data",
    default: true,
  },
  {
    id: "tactical",
    label: "Tactical Analysis",
    description: "PPDA, formations, pitch control",
    default: true,
  },
  {
    id: "phases",
    label: "Phase Breakdown",
    description: "Game phase statistics",
    default: true,
  },
  {
    id: "recommendations",
    label: "AI Recommendations",
    description: "Improvement suggestions",
    default: true,
  },
];

export function ReportGenerator({
  matchId,
  isOpen,
  onClose,
  className,
}: ReportGeneratorProps) {
  const [selectedSections, setSelectedSections] = useState<string[]>(
    SECTIONS.filter((s) => s.default).map((s) => s.id)
  );
  const [isGenerating, setIsGenerating] = useState(false);

  const toggleSection = (sectionId: string) => {
    setSelectedSections((prev) =>
      prev.includes(sectionId)
        ? prev.filter((id) => id !== sectionId)
        : [...prev, sectionId]
    );
  };

  const generatePdf = async () => {
    setIsGenerating(true);

    try {
      // Dynamic imports for PDF generation
      const jsPDF = (await import("jspdf")).default;

      const pdf = new jsPDF("p", "mm", "a4");
      const pageWidth = pdf.internal.pageSize.getWidth();
      let yOffset = 20;

      // Title
      pdf.setFontSize(24);
      pdf.setTextColor(59, 130, 246); // Primary blue
      pdf.text("Match Analysis Report", pageWidth / 2, yOffset, {
        align: "center",
      });
      yOffset += 15;

      // Match info
      pdf.setFontSize(14);
      pdf.setTextColor(100);
      pdf.text(`Match ID: ${matchId}`, pageWidth / 2, yOffset, {
        align: "center",
      });
      yOffset += 10;
      pdf.text(
        `Generated: ${new Date().toLocaleDateString()}`,
        pageWidth / 2,
        yOffset,
        { align: "center" }
      );
      yOffset += 20;

      // Sections
      pdf.setTextColor(0);

      if (selectedSections.includes("summary")) {
        pdf.setFontSize(16);
        pdf.setFont("helvetica", "bold");
        pdf.text("Executive Summary", 20, yOffset);
        yOffset += 10;

        pdf.setFontSize(11);
        pdf.setFont("helvetica", "normal");
        const summaryText =
          "The home team dominated possession and territory, maintaining consistent pressing intensity throughout the match. Key highlights include strong counter-attacking plays in the second half and effective defensive organization.";
        const lines = pdf.splitTextToSize(summaryText, pageWidth - 40);
        pdf.text(lines, 20, yOffset);
        yOffset += lines.length * 6 + 15;
      }

      if (selectedSections.includes("physical")) {
        pdf.setFontSize(16);
        pdf.setFont("helvetica", "bold");
        pdf.text("Physical Metrics", 20, yOffset);
        yOffset += 10;

        pdf.setFontSize(11);
        pdf.setFont("helvetica", "normal");
        pdf.text("• Total Team Distance: 112.4 km", 25, yOffset);
        yOffset += 7;
        pdf.text("• Average Speed: 7.2 km/h", 25, yOffset);
        yOffset += 7;
        pdf.text("• Total Sprints: 187", 25, yOffset);
        yOffset += 7;
        pdf.text("• High Intensity Runs: 423", 25, yOffset);
        yOffset += 15;
      }

      if (selectedSections.includes("tactical")) {
        pdf.setFontSize(16);
        pdf.setFont("helvetica", "bold");
        pdf.text("Tactical Analysis", 20, yOffset);
        yOffset += 10;

        pdf.setFontSize(11);
        pdf.setFont("helvetica", "normal");
        pdf.text("• PPDA Average: 9.2 (High Press)", 25, yOffset);
        yOffset += 7;
        pdf.text("• Pitch Control: 54% (Home)", 25, yOffset);
        yOffset += 7;
        pdf.text("• Formation: 4-3-3 → 4-4-2 (60')", 25, yOffset);
        yOffset += 7;
        pdf.text("• Defensive Line Height: 42m", 25, yOffset);
        yOffset += 15;
      }

      if (selectedSections.includes("phases")) {
        pdf.setFontSize(16);
        pdf.setFont("helvetica", "bold");
        pdf.text("Phase Breakdown", 20, yOffset);
        yOffset += 10;

        pdf.setFontSize(11);
        pdf.setFont("helvetica", "normal");
        pdf.text("• Organized Attack: 32%", 25, yOffset);
        yOffset += 7;
        pdf.text("• Organized Defense: 28%", 25, yOffset);
        yOffset += 7;
        pdf.text("• Transition Atk→Def: 22%", 25, yOffset);
        yOffset += 7;
        pdf.text("• Transition Def→Atk: 18%", 25, yOffset);
        yOffset += 15;
      }

      if (selectedSections.includes("recommendations")) {
        pdf.setFontSize(16);
        pdf.setFont("helvetica", "bold");
        pdf.text("AI Recommendations", 20, yOffset);
        yOffset += 10;

        pdf.setFontSize(11);
        pdf.setFont("helvetica", "normal");
        const recs = [
          "1. Improve transition speed when recovering possession",
          "2. Consider wider positioning in final third",
          "3. Increase pressing triggers in opponent half",
        ];
        recs.forEach((rec) => {
          pdf.text(rec, 25, yOffset);
          yOffset += 7;
        });
      }

      // Footer
      pdf.setFontSize(9);
      pdf.setTextColor(150);
      pdf.text(
        "Generated by AFTA - Football Intelligence Engine",
        pageWidth / 2,
        285,
        { align: "center" }
      );

      // Download
      pdf.save(`match-report-${matchId}.pdf`);
    } catch (error) {
      console.error("Failed to generate PDF:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <Card className={cn("w-full max-w-2xl glass animate-fade-in", className)}>
        <CardHeader className="border-b border-border/50">
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            Generate Report
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground mb-4">
            Select the sections to include in your PDF report:
          </p>

          {/* Section toggles */}
          <div className="space-y-3 mb-6">
            {SECTIONS.map((section) => (
              <button
                key={section.id}
                onClick={() => toggleSection(section.id)}
                className={cn(
                  "w-full flex items-center gap-3 p-3 rounded-lg border transition-colors text-left",
                  selectedSections.includes(section.id)
                    ? "border-primary bg-primary/10"
                    : "border-border hover:border-primary/50"
                )}
              >
                {selectedSections.includes(section.id) ? (
                  <CheckSquare className="h-5 w-5 text-primary shrink-0" />
                ) : (
                  <Square className="h-5 w-5 text-muted-foreground shrink-0" />
                )}
                <div>
                  <p className="font-medium">{section.label}</p>
                  <p className="text-sm text-muted-foreground">
                    {section.description}
                  </p>
                </div>
              </button>
            ))}
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button
              onClick={generatePdf}
              disabled={isGenerating || selectedSections.length === 0}
              className="gap-2"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4" />
                  Download PDF
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
