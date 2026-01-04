"use client";

import Link from "next/link";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Button,
  Skeleton,
} from "@/components/ui";
import {
  Activity,
  Video,
  Users,
  ChevronRight,
  Plus,
  Zap,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { useMatches, Match } from "@/src/api";

interface MatchCardProps {
  match: Match;
}

function MatchCard({ match }: MatchCardProps) {
  return (
    <Link href={`/matches/${match.match_id}`}>
      <Card className="glass glass-hover cursor-pointer transition-all hover:border-primary/50 group">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">
              {match.home_team_id} vs {match.away_team_id}
            </CardTitle>
            <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
          </div>
          <CardDescription>{match.date || "Date N/A"}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="text-2xl font-bold text-primary">
              {match.score || "-"}
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <Activity className="h-4 w-4" />
                {match.event_count} events
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

function MatchCardSkeleton() {
  return (
    <Card className="glass">
      <CardHeader className="pb-2">
        <Skeleton className="h-6 w-3/4" />
        <Skeleton className="h-4 w-1/3 mt-2" />
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-4 w-24" />
        </div>
      </CardContent>
    </Card>
  );
}

function EmptyState({ onRefresh }: { onRefresh: () => void }) {
  return (
    <div className="col-span-full flex flex-col items-center justify-center py-16 text-center">
      <Video className="h-16 w-16 text-muted-foreground mb-4" />
      <h3 className="text-xl font-medium mb-2">No Matches Found</h3>
      <p className="text-muted-foreground mb-6 max-w-md">
        No matches have been processed yet. Use the "Process Video" button to
        analyze a football match video.
      </p>
      <Button variant="outline" onClick={onRefresh}>
        <RefreshCw className="h-4 w-4 mr-2" />
        Refresh
      </Button>
    </div>
  );
}

function ErrorState({
  error,
  onRetry,
}: {
  error: string;
  onRetry: () => void;
}) {
  return (
    <div className="col-span-full flex flex-col items-center justify-center py-16 text-center">
      <AlertCircle className="h-16 w-16 text-destructive mb-4" />
      <h3 className="text-xl font-medium mb-2">Connection Error</h3>
      <p className="text-muted-foreground mb-2 max-w-md">
        Unable to connect to the backend API. Make sure the server is running on
        port 8000.
      </p>
      <p className="text-xs text-muted-foreground mb-6 font-mono">{error}</p>
      <Button variant="outline" onClick={onRetry}>
        <RefreshCw className="h-4 w-4 mr-2" />
        Retry
      </Button>
    </div>
  );
}

export default function Home() {
  // Fetch matches from API
  const { data: matches, isLoading, isError, error, refetch } = useMatches();

  // Calculate stats
  const totalPlayers = (matches?.length || 0) * 22;
  const totalEvents = matches?.reduce((acc, m) => acc + m.event_count, 0) || 0;

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/50 glass sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-primary/20 flex items-center justify-center">
              <Zap className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold">AFTA</h1>
              <p className="text-xs text-muted-foreground">
                Football Intelligence Engine
              </p>
            </div>
          </div>
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Process Video
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card className="glass">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-lg bg-primary/20 flex items-center justify-center">
                  <Video className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{matches?.length || 0}</p>
                  <p className="text-sm text-muted-foreground">
                    Matches Analyzed
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="glass">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-lg bg-green-500/20 flex items-center justify-center">
                  <Users className="h-6 w-6 text-green-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{totalPlayers}</p>
                  <p className="text-sm text-muted-foreground">
                    Players Tracked
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="glass">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-lg bg-purple-500/20 flex items-center justify-center">
                  <Activity className="h-6 w-6 text-purple-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold" suppressHydrationWarning>
                    {totalEvents.toLocaleString()}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Events Processed
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Matches Section */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold mb-2">Recent Matches</h2>
          <p className="text-muted-foreground">
            Select a match to view detailed analysis
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {isLoading ? (
            <>
              <MatchCardSkeleton />
              <MatchCardSkeleton />
              <MatchCardSkeleton />
            </>
          ) : isError ? (
            <ErrorState
              error={(error as Error)?.message || "Unknown error"}
              onRetry={() => refetch()}
            />
          ) : matches && matches.length > 0 ? (
            matches.map((match) => (
              <MatchCard key={match.match_id} match={match} />
            ))
          ) : (
            <EmptyState onRefresh={() => refetch()} />
          )}
        </div>
      </div>
    </main>
  );
}
