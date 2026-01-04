# Implementation Plan: Video Player Component

> **Reference Spec:** [02_video_player_spec.md](./02_video_player_spec.md)

## Overview

Interactive video player with drawing overlay and frame-by-frame navigation. Core component for tactical review sessions.

---

## Design Reference

Based on mockups:

- **Player:** Full-width video with custom controls bar
- **Timeline:** Scrubber with phase markers
- **Drawing:** Floating toolbar for annotation tools
- **Controls:** Play/pause, speed selector, frame navigation

---

## Component Structure

```
components/video-player/
├── VideoPlayer.tsx        # Main container
├── VideoControls.tsx      # Custom control bar
├── DrawingCanvas.tsx      # Annotation overlay
├── DrawingToolbar.tsx     # Tool selection
├── Timeline.tsx           # Seek bar with markers
└── SpeedSelector.tsx      # Playback speed dropdown
```

---

## Implementation Steps

### 1. VideoPlayer Container

```tsx
interface VideoPlayerProps {
  videoUrl: string;
  onTimeUpdate?: (time: number) => void;
}
```

- Integrate `react-player` with refs for programmatic control
- Layer structure: Video → Canvas → Controls
- Sync `currentTimestamp` to Zustand on progress

### 2. Custom Controls

```tsx
<VideoControls>
  <PlayPauseButton />
  <Timeline progress={progress} onSeek={handleSeek} />
  <TimeDisplay current={current} duration={duration} />
  <SpeedSelector value={speed} onChange={setSpeed} />
  <FrameNavButtons onPrev={prevFrame} onNext={nextFrame} />
</VideoControls>
```

- Play/Pause with space bar hotkey
- Timeline with hover preview
- Speed options: 0.25x, 0.5x, 1x, 1.5x, 2x
- Frame-by-frame: Left/Right arrow keys (±1 frame at 25fps)

### 3. Drawing Canvas

```tsx
interface Drawing {
  id: string;
  type: "line" | "arrow" | "circle" | "freehand";
  points: { x: number; y: number }[];
  color: string;
  timestamp: number;
}
```

- HTML5 Canvas overlaying video
- Store drawings keyed by timestamp (±100ms tolerance)
- Tools: Line, Arrow, Circle, Freehand, Eraser
- Colors: Blue, Red, Yellow, White
- Clear all button

### 4. Drawing Toolbar

Floating toolbar with:

- Tool icons (Line, Arrow, Circle, Freehand)
- Color picker
- Stroke width
- Undo/Clear buttons

### 5. Keyboard Shortcuts

| Key         | Action              |
| ----------- | ------------------- |
| Space       | Play/Pause          |
| Left Arrow  | Previous frame      |
| Right Arrow | Next frame          |
| [           | Decrease speed      |
| ]           | Increase speed      |
| D           | Toggle drawing mode |
| Escape      | Exit drawing mode   |

---

## State Management

```typescript
// Local component state
const [drawings, setDrawings] = useState<Map<number, Drawing[]>>(new Map());
const [activeTool, setActiveTool] = useState<Tool>("arrow");
const [isDrawing, setIsDrawing] = useState(false);

// Global store sync
const { setCurrentTimestamp, setCurrentFrame, isPlaying } = useMatchStore();
```

---

## Verification

- [ ] Video loads and plays MP4 files
- [ ] Custom controls work (seek, speed, frame nav)
- [ ] Drawings persist when scrubbing back to timestamp
- [ ] Keyboard shortcuts function
- [ ] Canvas resizes with video
