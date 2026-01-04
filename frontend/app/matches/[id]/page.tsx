"use client";

import { useParams, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { useMatchStore } from "@/src/store";
import { useMatch } from "@/src/api";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  Skeleton,
  Progress,
} from "@/components/ui";
import {
  ArrowLeft,
  Download,
  Settings,
  Share2,
  Loader2,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import Link from "next/link";
import { apiClient } from "@/src/api";

// Dynamic imports with ssr:false to prevent hydration issues
const VideoPlayer = dynamic(
  () =>
    import("@/components/video-player/VideoPlayer").then(
      (mod) => mod.VideoPlayer
    ),
  {
    ssr: false,
    loading: () => (
      <div className="h-full flex items-center justify-center">
        <Skeleton className="h-full w-full" />
      </div>
    ),
  }
);

const TacticalBoard = dynamic(
  () =>
    import("@/components/pitch-view/TacticalBoard").then(
      (mod) => mod.TacticalBoard
    ),
  {
    ssr: false,
    loading: () => (
      <div className="h-full flex items-center justify-center">
        <Skeleton className="h-full w-full" />
      </div>
    ),
  }
);

const MetricsPanel = dynamic(
  () =>
    import("@/components/metrics/MetricsPanel").then((mod) => mod.MetricsPanel),
  {
    ssr: false,
    loading: () => (
      <div className="h-full flex items-center justify-center">
        <Skeleton className="h-full w-full" />
      </div>
    ),
  }
);

const ChatInterface = dynamic(
  () =>
    import("@/components/chat/ChatInterface").then((mod) => mod.ChatInterface),
  {
    ssr: false,
    loading: () => (
      <div className="h-full flex items-center justify-center">
        <Skeleton className="h-full w-full" />
      </div>
    ),
  }
);

// Processing status banner component
function ProcessingBanner({ matchId }: { matchId: string }) {
  const [jobInfo, setJobInfo] = useState<{
    jobId: string;
    status: string;
    progress?: number;
    message?: string;
  } | null>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    // Check localStorage for job info
    const stored = localStorage.getItem(`processing-job-${matchId}`);
    if (!stored) return;

    try {
      const { jobId, startedAt } = JSON.parse(stored);

      // Ignore jobs older than 1 hour
      if (Date.now() - startedAt > 3600000) {
        localStorage.removeItem(`processing-job-${matchId}`);
        return;
      }

      // Poll for status
      const pollStatus = async () => {
        try {
          const { data } = await apiClient.get(`/video/job/${jobId}`);
          setJobInfo({
            jobId,
            status: data.status,
            progress: data.progress,
            message: data.message,
          });

          // Clear localStorage when complete or failed
          if (data.status === "completed" || data.status === "failed") {
            localStorage.removeItem(`processing-job-${matchId}`);
          }
        } catch (error) {
          console.error("Failed to fetch job status:", error);
        }
      };

      pollStatus();
      const interval = setInterval(pollStatus, 3000);

      return () => clearInterval(interval);
    } catch (e) {
      console.error("Failed to parse job info:", e);
    }
  }, [matchId]);

  if (!jobInfo || dismissed) return null;

  const isComplete = jobInfo.status === "completed";
  const isFailed = jobInfo.status === "failed";
  const isProcessing =
    jobInfo.status === "processing" || jobInfo.status === "queued";

  return (
    <div
      className={`border-b px-4 py-3 ${
        isComplete
          ? "bg-green-500/10 border-green-500/30"
          : isFailed
          ? "bg-destructive/10 border-destructive/30"
          : "bg-primary/10 border-primary/30"
      }`}
    >
      <div className="container mx-auto flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1">
          {isComplete ? (
            <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
          ) : isFailed ? (
            <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0" />
          ) : (
            <Loader2 className="h-5 w-5 text-primary animate-spin flex-shrink-0" />
          )}
          <div className="flex-1">
            <p className="text-sm font-medium">
              {isComplete
                ? "Video Processing Complete!"
                : isFailed
                ? "Processing Failed"
                : "Processing Video..."}
            </p>
            <p className="text-xs text-muted-foreground">
              {jobInfo.message || "Please wait while we analyze the video"}
            </p>
          </div>
          {isProcessing && jobInfo.progress !== undefined && (
            <div className="w-32">
              <Progress value={jobInfo.progress} className="h-2" />
            </div>
          )}
        </div>
        {(isComplete || isFailed) && (
          <Button variant="ghost" size="sm" onClick={() => setDismissed(true)}>
            Dismiss
          </Button>
        )}
      </div>
    </div>
  );
}

export default function MatchDetailPage() {
  const params = useParams();
  const matchId = params.id as string;
  const [mounted, setMounted] = useState(false);

  // Global state
  const { setMatchId, reset } = useMatchStore();

  // Set mounted and match context on mount
  useEffect(() => {
    setMounted(true);
    setMatchId(matchId);
    return () => reset();
  }, [matchId, setMatchId, reset]);

  // Fetch match data
  const { data: match, isLoading: matchLoading } = useMatch(matchId);

  // Don't render until mounted to prevent hydration mismatch
  if (!mounted) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Skeleton className="h-12 w-48" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Processing Status Banner */}
      <ProcessingBanner matchId={matchId} />

      {/* Header */}
      <header className="border-b border-border/50 glass sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div>
              {matchLoading ? (
                <>
                  <Skeleton className="h-6 w-48 mb-1" />
                  <Skeleton className="h-4 w-32" />
                </>
              ) : (
                <>
                  <h1 className="text-lg font-bold">
                    {match?.home_team_id || "Home"} vs{" "}
                    {match?.away_team_id || "Away"}
                  </h1>
                  <p className="text-sm text-muted-foreground">
                    Match Analysis • {match?.event_count || 0} events
                  </p>
                </>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" className="gap-2">
              <Share2 className="h-4 w-4" />
              Share
            </Button>
            <Button variant="outline" size="sm" className="gap-2">
              <Download className="h-4 w-4" />
              Export
            </Button>
            <Button variant="ghost" size="icon">
              <Settings className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content - 4 Panel Grid */}
      <main className="flex-1 container mx-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-[calc(100vh-120px)]">
          {/* Top Left - Video Player */}
          <Card className="glass overflow-hidden">
            <CardHeader className="py-3 px-4 border-b border-border/50">
              <CardTitle className="text-sm font-medium">
                Video Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0 h-[calc(100%-52px)]">
              <VideoPlayer
                videoUrl={`http://localhost:8000/api/v1/video/${matchId}/stream`}
                matchId={matchId}
              />
            </CardContent>
          </Card>

          {/* Top Right - Tactical Board */}
          <Card className="glass overflow-hidden">
            <CardHeader className="py-3 px-4 border-b border-border/50">
              <CardTitle className="text-sm font-medium">
                Tactical View
              </CardTitle>
            </CardHeader>
            <CardContent className="p-2 h-[calc(100%-52px)]">
              <TacticalBoard matchId={matchId} />
            </CardContent>
          </Card>

          {/* Bottom Left - Metrics */}
          <Card className="glass overflow-hidden">
            <CardHeader className="py-3 px-4 border-b border-border/50">
              <CardTitle className="text-sm font-medium">
                Performance Metrics
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 h-[calc(100%-52px)] overflow-auto">
              <MetricsPanel matchId={matchId} />
            </CardContent>
          </Card>

          {/* Bottom Right - Chat */}
          <Card className="glass overflow-hidden flex flex-col">
            <CardHeader className="py-3 px-4 border-b border-border/50">
              <CardTitle className="text-sm font-medium">AI Analysis</CardTitle>
            </CardHeader>
            <CardContent className="p-0 flex-1 overflow-hidden">
              <ChatInterface matchId={matchId} />
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
