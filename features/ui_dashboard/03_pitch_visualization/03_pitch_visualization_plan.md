# Implementation Plan: Pitch Visualization Component

> **Reference Spec:** [03_pitch_visualization_spec.md](./03_pitch_visualization_spec.md)

## Overview

Interactive 2D top-down pitch view showing player positions, heatmaps, and Voronoi diagrams synchronized with video playback.

---

## Design Reference

Based on mockups:

- **Pitch:** Dark green with white line markings
- **Players:** Colored circles with jersey numbers
- **Heatmap:** Semi-transparent overlay (Blue/Red diverging)
- **Controls:** Layer toggles in corner

---

## Component Structure

```
components/pitch-view/
├── TacticalBoard.tsx      # Main SVG container
├── PitchMarkings.tsx      # Lines, circles, boxes
├── PlayerDots.tsx         # Player positions
├── BallIndicator.tsx      # Ball position
├── HeatmapLayer.tsx       # Pitch control heatmap
├── VoronoiLayer.tsx       # Space control tessellation
└── LayerToggles.tsx       # Visibility controls
```

---

## Implementation Steps

### 1. TacticalBoard Container

```tsx
interface TacticalBoardProps {
  trackingData: TrackingFrame[];
  pitchControl?: PitchControlGrid;
  className?: string;
}
```

- SVG with viewBox `0 0 105 68` (pitch dimensions in meters)
- ResponsiveContainer wrapper for scaling
- Subscribe to `currentFrame` from Zustand

### 2. Pitch Markings (SVG)

Standard football pitch elements:

- Outer boundary
- Center circle (radius 9.15m)
- Center line
- Penalty areas (16.5m × 40.3m)
- Goal areas (5.5m × 18.3m)
- Penalty spots (11m from goal line)
- Corner arcs

```tsx
<svg viewBox="0 0 105 68" className="pitch-svg">
  {/* Background */}
  <rect fill="#1a472a" width="105" height="68" />

  {/* Lines */}
  <rect
    stroke="#fff"
    strokeWidth="0.12"
    fill="none"
    x="0"
    y="0"
    width="105"
    height="68"
  />
  <line stroke="#fff" x1="52.5" y1="0" x2="52.5" y2="68" />
  <circle stroke="#fff" cx="52.5" cy="34" r="9.15" fill="none" />
  {/* ... penalty areas, goal areas */}
</svg>
```

### 3. Player Dots

```tsx
interface PlayerDotProps {
  player: {
    player_id: string;
    x: number;
    y: number;
    team: "home" | "away";
    jersey_number?: number;
  };
}
```

- Circle with team color (home=blue, away=red)
- Jersey number text inside
- Hover tooltip with player name/stats
- Click to highlight in metrics

### 4. Heatmap Layer

Pitch Control visualization using grid cells:

```tsx
<g className="heatmap-layer" opacity={0.6}>
  {grid.map((cell) => (
    <rect
      key={`${cell.x}-${cell.y}`}
      x={cell.x}
      y={cell.y}
      width={cellSize}
      height={cellSize}
      fill={interpolateRdBu(cell.homeControl)}
    />
  ))}
</g>
```

- Use d3-scale-chromatic for color interpolation
- Blue (home control) → White (50/50) → Red (away control)
- Fetch from `/matches/{id}/metrics` pitch_control data

### 5. Voronoi Layer

Space tessellation based on player positions:

```tsx
import { Delaunay } from "d3-delaunay";

const delaunay = Delaunay.from(players.map((p) => [p.x, p.y]));
const voronoi = delaunay.voronoi([0, 0, 105, 68]);
```

- Render Voronoi cells as polygons
- Color by player team
- Lower opacity (0.3) to not obscure players

### 6. Layer Toggles

Toggle buttons panel:

```tsx
<div className="absolute top-2 right-2 flex gap-1">
  <ToggleButton
    active={showPlayerDots}
    onClick={togglePlayerDots}
    icon={<Users />}
    label="Players"
  />
  <ToggleButton
    active={showHeatmap}
    onClick={toggleHeatmap}
    icon={<Flame />}
    label="Heatmap"
  />
  <ToggleButton
    active={showVoronoi}
    onClick={toggleVoronoi}
    icon={<Grid />}
    label="Voronoi"
  />
</div>
```

---

## Frame Synchronization

```typescript
const { currentFrame } = useMatchStore();

// Find tracking data for current frame
const frameData = useMemo(() => {
  return trackingData.find((f) => f.frame_id === currentFrame);
}, [trackingData, currentFrame]);
```

- Update player positions on frame change
- Smooth transitions with CSS (optional)
- Handle missing frames gracefully

---

## Verification

- [ ] Pitch renders with correct proportions
- [ ] Players appear at correct positions
- [ ] Heatmap displays pitch control
- [ ] Voronoi tessellation renders
- [ ] Layer toggles work
- [ ] Syncs with video timestamp (±100ms)
- [ ] Responsive scaling on window resize
