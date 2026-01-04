"use client";

import { useMemo } from "react";
import { useMatchStore } from "@/src/store";
import { Button } from "@/components/ui";
import { Users, Flame, Grid3X3, Eye, EyeOff } from "lucide-react";
import { cn, TEAM_COLORS, pitchToSvg, PITCH_DIMENSIONS } from "@/src/utils";

interface Player {
  player_id: string;
  x: number;
  y: number;
  team: "home" | "away";
  jersey_number?: number;
}

interface TacticalBoardProps {
  matchId: string;
  className?: string;
}

// Demo player positions - replace with real tracking data
const DEMO_PLAYERS: Player[] = [
  // Home Team (in attack)
  { player_id: "h1", x: 10, y: 34, team: "home", jersey_number: 1 },
  { player_id: "h2", x: 25, y: 10, team: "home", jersey_number: 2 },
  { player_id: "h3", x: 25, y: 25, team: "home", jersey_number: 4 },
  { player_id: "h4", x: 25, y: 43, team: "home", jersey_number: 5 },
  { player_id: "h5", x: 25, y: 58, team: "home", jersey_number: 3 },
  { player_id: "h6", x: 45, y: 17, team: "home", jersey_number: 6 },
  { player_id: "h7", x: 50, y: 34, team: "home", jersey_number: 8 },
  { player_id: "h8", x: 45, y: 51, team: "home", jersey_number: 10 },
  { player_id: "h9", x: 70, y: 20, team: "home", jersey_number: 7 },
  { player_id: "h10", x: 75, y: 34, team: "home", jersey_number: 9 },
  { player_id: "h11", x: 70, y: 48, team: "home", jersey_number: 11 },
  // Away Team (in defense)
  { player_id: "a1", x: 95, y: 34, team: "away", jersey_number: 1 },
  { player_id: "a2", x: 80, y: 15, team: "away", jersey_number: 2 },
  { player_id: "a3", x: 82, y: 28, team: "away", jersey_number: 4 },
  { player_id: "a4", x: 82, y: 40, team: "away", jersey_number: 5 },
  { player_id: "a5", x: 80, y: 53, team: "away", jersey_number: 3 },
  { player_id: "a6", x: 65, y: 20, team: "away", jersey_number: 6 },
  { player_id: "a7", x: 60, y: 34, team: "away", jersey_number: 8 },
  { player_id: "a8", x: 65, y: 48, team: "away", jersey_number: 10 },
  { player_id: "a9", x: 55, y: 25, team: "away", jersey_number: 7 },
  { player_id: "a10", x: 50, y: 50, team: "away", jersey_number: 9 },
  { player_id: "a11", x: 58, y: 58, team: "away", jersey_number: 11 },
];

const BALL_POSITION = { x: 72, y: 32 };

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

  // Use demo data for now - in production, fetch from API based on currentFrame
  const players = useMemo(() => DEMO_PLAYERS, []);
  const ball = useMemo(() => BALL_POSITION, []);

  return (
    <div className={cn("relative h-full flex flex-col", className)}>
      {/* Layer toggles */}
      <div className="absolute top-2 right-2 z-10 flex gap-1">
        <Button
          variant={showPlayerDots ? "default" : "outline"}
          size="sm"
          className="h-8 px-2"
          onClick={togglePlayerDots}
        >
          <Users className="h-4 w-4" />
        </Button>
        <Button
          variant={showHeatmap ? "default" : "outline"}
          size="sm"
          className="h-8 px-2"
          onClick={toggleHeatmap}
        >
          <Flame className="h-4 w-4" />
        </Button>
        <Button
          variant={showVoronoi ? "default" : "outline"}
          size="sm"
          className="h-8 px-2"
          onClick={toggleVoronoi}
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

        {/* Heatmap layer placeholder */}
        {showHeatmap && (
          <g className="heatmap-layer" opacity={0.4}>
            {/* Simplified gradient heatmap */}
            <defs>
              <linearGradient id="heatmapGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.8" />
                <stop offset="50%" stopColor="#ffffff" stopOpacity="0.2" />
                <stop offset="100%" stopColor="#ef4444" stopOpacity="0.8" />
              </linearGradient>
            </defs>
            <rect
              x="0"
              y="0"
              width="105"
              height="68"
              fill="url(#heatmapGradient)"
            />
          </g>
        )}

        {/* Voronoi layer placeholder */}
        {showVoronoi && (
          <g className="voronoi-layer" opacity={0.2}>
            {/* Simplified voronoi representation */}
            {players.map((player) => (
              <circle
                key={`voronoi-${player.player_id}`}
                cx={player.x}
                cy={player.y}
                r={8}
                fill={player.team === "home" ? "#3b82f6" : "#ef4444"}
                opacity={0.3}
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
            <circle
              cx={ball.x}
              cy={ball.y}
              r={1}
              fill="#fbbf24"
              stroke="white"
              strokeWidth="0.2"
            />
          </g>
        )}
      </svg>

      {/* Frame indicator */}
      <div className="absolute bottom-2 left-2 text-xs text-muted-foreground bg-black/50 px-2 py-1 rounded">
        Frame: {currentFrame}
      </div>
    </div>
  );
}
