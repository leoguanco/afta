"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { useMatchStore } from "@/src/store";
import { useMatch, useMatchPhases } from "@/src/api";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  Skeleton,
} from "@/components/ui";
import { ArrowLeft, Download, Settings, Share2 } from "lucide-react";
import Link from "next/link";

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
