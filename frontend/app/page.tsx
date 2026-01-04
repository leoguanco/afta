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
import { Activity, Video, Users, ChevronRight, Plus, Zap } from "lucide-react";
import { useMatches, Match } from "@/src/api";

// Demo matches as fallback when API is not available
const DEMO_MATCHES: Match[] = [
  {
    match_id: "match-001",
    home_team_id: "Boca Juniors",
    away_team_id: "River Plate",
    event_count: 1247,
    date: "2025-12-28",
    score: "2 - 1",
  },
  {
    match_id: "match-002",
    home_team_id: "Barcelona",
    away_team_id: "Real Madrid",
    event_count: 982,
    date: "2025-12-20",
    score: "3 - 2",
  },
  {
    match_id: "match-003",
    home_team_id: "Manchester City",
    away_team_id: "Liverpool",
    event_count: 1105,
    date: "2025-12-15",
    score: "1 - 1",
  },
];

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

export default function Home() {
  // Fetch matches from API, falls back to demo data on error
  const { data: apiMatches, isLoading, isError } = useMatches();

  // Use API data if available, otherwise use demo data
  const matches =
    apiMatches && apiMatches.length > 0 ? apiMatches : DEMO_MATCHES;
  const showingDemoData = !apiMatches || apiMatches.length === 0;

  // Calculate stats
  const totalPlayers = matches.length * 22; // Approximate
  const totalEvents = matches.reduce((acc, m) => acc + m.event_count, 0);

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
        {/* Demo data notice */}
        {showingDemoData && !isLoading && (
          <div className="mb-6 p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30 text-yellow-200 text-sm">
            <strong>Demo Mode:</strong> Showing sample data. Start the backend
            API on port 8000 to see real matches.
          </div>
        )}

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card className="glass">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-lg bg-primary/20 flex items-center justify-center">
                  <Video className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{matches.length}</p>
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
          ) : (
            matches.map((match) => (
              <MatchCard key={match.match_id} match={match} />
            ))
          )}
        </div>
      </div>
    </main>
  );
}
