"use client";

import { useMemo } from "react";
import { useMatchStore } from "@/src/store";
import { useTrackingData } from "@/src/api";
import { Button, Skeleton } from "@/components/ui";
import { Users, Flame, Grid3X3, RefreshCw } from "lucide-react";
import { cn } from "@/src/utils";

interface TacticalBoardProps {
  matchId: string;
  className?: string;
}

export function TacticalBoard({ matchId, className }: TacticalBoardProps) {
  const {
    showPlayerDots,
    showHeatmap,
    showVoronoi,
    togglePlayerDots,
    toggleHeatmap,
    toggleVoronoi,
    currentFrame,
  } = useMatchStore();

  // Fetch real tracking data from API
  const {
    data: trackingData,
    isLoading,
    isError,
    refetch,
  } = useTrackingData(matchId, currentFrame, currentFrame + 1);

  // Get current frame data
  const frameData = useMemo(() => {
    if (!trackingData || trackingData.length === 0) return null;
    return trackingData[0];
  }, [trackingData]);

  // Extract players and ball from frame data
  const players = useMemo(() => {
    if (!frameData?.players) return [];
    return frameData.players.map((p) => ({
      player_id: p.player_id,
      x: p.x,
      y: p.y,
      team: p.team,
      jersey_number: p.jersey_number,
    }));
  }, [frameData]);

  const ball = useMemo(() => {
    return frameData?.ball || null;
  }, [frameData]);

  // Show loading state
  if (isLoading && !frameData) {
    return (
      <div
        className={cn(
          "relative h-full flex items-center justify-center",
          className
        )}
      >
        <div className="text-center">
          <Skeleton className="h-full w-full absolute inset-0" />
          <p className="text-muted-foreground">Loading tracking data...</p>
        </div>
      </div>
    );
  }

  // Show error/no data state
  if (isError || !frameData) {
    return (
      <div
        className={cn(
          "relative h-full flex flex-col items-center justify-center",
          className
        )}
      >
        <p className="text-muted-foreground mb-4">
          No tracking data available for this frame
        </p>
        <p className="text-xs text-muted-foreground mb-4">
          Run video processing to generate tracking data
        </p>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className={cn("relative h-full flex flex-col", className)}>
      {/* Layer toggles */}
      <div className="absolute top-2 right-2 z-10 flex gap-1">
        <Button
          variant={showPlayerDots ? "default" : "outline"}
          size="sm"
          className="h-8 px-2"
          onClick={togglePlayerDots}
          title="Toggle Players"
        >
          <Users className="h-4 w-4" />
        </Button>
        <Button
          variant={showHeatmap ? "default" : "outline"}
          size="sm"
          className="h-8 px-2"
          onClick={toggleHeatmap}
          title="Toggle Heatmap"
        >
          <Flame className="h-4 w-4" />
        </Button>
        <Button
          variant={showVoronoi ? "default" : "outline"}
          size="sm"
          className="h-8 px-2"
          onClick={toggleVoronoi}
          title="Toggle Voronoi"
        >
          <Grid3X3 className="h-4 w-4" />
        </Button>
      </div>

      {/* Pitch SVG */}
      <svg
        viewBox="0 0 105 68"
        className="flex-1 w-full"
        style={{ background: "hsl(145 63% 15%)" }}
      >
        {/* Pitch markings */}
        <g stroke="rgba(255,255,255,0.6)" strokeWidth="0.15" fill="none">
          {/* Outer boundary */}
          <rect x="0" y="0" width="105" height="68" />

          {/* Center line */}
          <line x1="52.5" y1="0" x2="52.5" y2="68" />

          {/* Center circle */}
          <circle cx="52.5" cy="34" r="9.15" />

          {/* Center spot */}
          <circle cx="52.5" cy="34" r="0.3" fill="rgba(255,255,255,0.6)" />

          {/* Left penalty area */}
          <rect x="0" y="13.84" width="16.5" height="40.32" />

          {/* Left goal area */}
          <rect x="0" y="24.84" width="5.5" height="18.32" />

          {/* Left penalty spot */}
          <circle cx="11" cy="34" r="0.3" fill="rgba(255,255,255,0.6)" />

          {/* Left penalty arc */}
          <path d="M 16.5 27.2 A 9.15 9.15 0 0 1 16.5 40.8" />

          {/* Right penalty area */}
          <rect x="88.5" y="13.84" width="16.5" height="40.32" />

          {/* Right goal area */}
          <rect x="99.5" y="24.84" width="5.5" height="18.32" />

          {/* Right penalty spot */}
          <circle cx="94" cy="34" r="0.3" fill="rgba(255,255,255,0.6)" />

          {/* Right penalty arc */}
          <path d="M 88.5 27.2 A 9.15 9.15 0 0 0 88.5 40.8" />

          {/* Corner arcs */}
          <path d="M 1 0 A 1 1 0 0 0 0 1" />
          <path d="M 104 0 A 1 1 0 0 1 105 1" />
          <path d="M 0 67 A 1 1 0 0 0 1 68" />
          <path d="M 105 67 A 1 1 0 0 1 104 68" />

          {/* Goals */}
          <rect
            x="-2"
            y="30.34"
            width="2"
            height="7.32"
            stroke="white"
            strokeWidth="0.2"
          />
          <rect
            x="105"
            y="30.34"
            width="2"
            height="7.32"
            stroke="white"
            strokeWidth="0.2"
          />
        </g>

        {/* Heatmap layer */}
        {showHeatmap && players.length > 0 && (
          <g className="heatmap-layer" opacity={0.3}>
            {players.map((player) => (
              <circle
                key={`heat-${player.player_id}`}
                cx={player.x}
                cy={player.y}
                r={10}
                fill={player.team === "home" ? "#3b82f6" : "#ef4444"}
                opacity={0.3}
              />
            ))}
          </g>
        )}

        {/* Voronoi layer */}
        {showVoronoi && players.length > 0 && (
          <g className="voronoi-layer" opacity={0.15}>
            {players.map((player) => (
              <circle
                key={`voronoi-${player.player_id}`}
                cx={player.x}
                cy={player.y}
                r={12}
                fill={player.team === "home" ? "#3b82f6" : "#ef4444"}
              />
            ))}
          </g>
        )}

        {/* Player dots */}
        {showPlayerDots && (
          <g className="players-layer">
            {players.map((player) => (
              <g key={player.player_id}>
                {/* Player circle */}
                <circle
                  cx={player.x}
                  cy={player.y}
                  r={2}
                  fill={player.team === "home" ? "#3b82f6" : "#ef4444"}
                  stroke="white"
                  strokeWidth="0.3"
                />
                {/* Jersey number */}
                {player.jersey_number && (
                  <text
                    x={player.x}
                    y={player.y + 0.6}
                    textAnchor="middle"
                    fontSize="1.8"
                    fill="white"
                    fontWeight="bold"
                  >
                    {player.jersey_number}
                  </text>
                )}
              </g>
            ))}

            {/* Ball */}
            {ball && (
              <circle
                cx={ball.x}
                cy={ball.y}
                r={1}
                fill="#fbbf24"
                stroke="white"
                strokeWidth="0.2"
              />
            )}
          </g>
        )}
      </svg>

      {/* Frame indicator */}
      <div className="absolute bottom-2 left-2 text-xs text-muted-foreground bg-black/50 px-2 py-1 rounded flex items-center gap-2">
        <span>Frame: {currentFrame}</span>
        <span>|</span>
        <span>Players: {players.length}</span>
      </div>
    </div>
  );
}
