"use client";

import { useRef, useState, useCallback, useEffect } from "react";
import ReactPlayer from "react-player";
import { useMatchStore } from "@/src/store";
import { Button } from "@/components/ui";
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  ChevronLeft,
  ChevronRight,
  Pencil,
  Maximize2,
} from "lucide-react";
import { cn, formatTime } from "@/src/utils";

interface VideoPlayerProps {
  videoUrl: string;
  matchId: string;
  className?: string;
}

export function VideoPlayer({
  videoUrl,
  matchId,
  className,
}: VideoPlayerProps) {
  const playerRef = useRef<ReactPlayer>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Global state
  const {
    isPlaying,
    setIsPlaying,
    playbackSpeed,
    setPlaybackSpeed,
    setCurrentTimestamp,
    setCurrentFrame,
  } = useMatchStore();

  // Local state
  const [duration, setDuration] = useState(0);
  const [progress, setProgress] = useState(0);
  const [seeking, setSeeking] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const [isDrawingMode, setIsDrawingMode] = useState(false);

  const FPS = 25;

  // Handle progress updates
  const handleProgress = useCallback(
    (state: { played: number; playedSeconds: number }) => {
      if (!seeking) {
        setProgress(state.played);
        setCurrentTimestamp(state.playedSeconds);
        setCurrentFrame(Math.floor(state.playedSeconds * FPS));
      }
    },
    [seeking, setCurrentTimestamp, setCurrentFrame]
  );

  // Handle seeking
  const handleSeek = useCallback((value: number) => {
    setProgress(value);
    playerRef.current?.seekTo(value, "fraction");
  }, []);

  // Frame navigation
  const nextFrame = useCallback(() => {
    const current = playerRef.current?.getCurrentTime() || 0;
    const newTime = current + 1 / FPS;
    playerRef.current?.seekTo(newTime, "seconds");
  }, []);

  const prevFrame = useCallback(() => {
    const current = playerRef.current?.getCurrentTime() || 0;
    const newTime = Math.max(0, current - 1 / FPS);
    playerRef.current?.seekTo(newTime, "seconds");
  }, []);

  // Skip forward/back
  const skipForward = useCallback(() => {
    const current = playerRef.current?.getCurrentTime() || 0;
    playerRef.current?.seekTo(current + 10, "seconds");
  }, []);

  const skipBack = useCallback(() => {
    const current = playerRef.current?.getCurrentTime() || 0;
    playerRef.current?.seekTo(Math.max(0, current - 10), "seconds");
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement) return;

      switch (e.key) {
        case " ":
          e.preventDefault();
          setIsPlaying(!isPlaying);
          break;
        case "ArrowLeft":
          e.preventDefault();
          if (e.shiftKey) skipBack();
          else prevFrame();
          break;
        case "ArrowRight":
          e.preventDefault();
          if (e.shiftKey) skipForward();
          else nextFrame();
          break;
        case "d":
        case "D":
          setIsDrawingMode((prev) => !prev);
          break;
        case "[":
          setPlaybackSpeed(Math.max(0.25, playbackSpeed - 0.25));
          break;
        case "]":
          setPlaybackSpeed(Math.min(2, playbackSpeed + 0.25));
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [
    isPlaying,
    playbackSpeed,
    setIsPlaying,
    setPlaybackSpeed,
    skipBack,
    skipForward,
    prevFrame,
    nextFrame,
  ]);

  // Current time display
  const currentTime = playerRef.current?.getCurrentTime() || 0;

  return (
    <div
      ref={containerRef}
      className={cn("relative flex flex-col h-full bg-black", className)}
      onMouseEnter={() => setShowControls(true)}
      onMouseLeave={() => !isPlaying && setShowControls(true)}
    >
      {/* Video */}
      <div className="flex-1 relative">
        <ReactPlayer
          ref={playerRef}
          url={videoUrl}
          width="100%"
          height="100%"
          playing={isPlaying}
          playbackRate={playbackSpeed}
          onDuration={setDuration}
          onProgress={handleProgress}
          progressInterval={40} // ~25fps update rate
          config={{
            file: {
              attributes: {
                crossOrigin: "anonymous",
              },
            },
          }}
        />

        {/* Drawing overlay indicator */}
        {isDrawingMode && (
          <div className="absolute top-4 left-4 bg-red-500/80 text-white px-3 py-1 rounded-full text-sm flex items-center gap-2">
            <Pencil className="h-4 w-4" />
            Drawing Mode
          </div>
        )}

        {/* No video placeholder */}
        {!videoUrl && (
          <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <Play className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No video loaded</p>
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div
        className={cn(
          "bg-gradient-to-t from-black/90 to-transparent p-4 transition-opacity",
          showControls ? "opacity-100" : "opacity-0"
        )}
      >
        {/* Progress bar */}
        <div className="mb-3">
          <input
            type="range"
            min={0}
            max={1}
            step={0.001}
            value={progress}
            onChange={(e) => {
              setSeeking(true);
              handleSeek(parseFloat(e.target.value));
            }}
            onMouseUp={() => setSeeking(false)}
            onTouchEnd={() => setSeeking(false)}
            className="w-full h-1 bg-muted rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary"
          />
        </div>

        {/* Controls row */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {/* Play/Pause */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsPlaying(!isPlaying)}
            >
              {isPlaying ? (
                <Pause className="h-5 w-5" />
              ) : (
                <Play className="h-5 w-5" />
              )}
            </Button>

            {/* Skip back */}
            <Button variant="ghost" size="icon" onClick={skipBack}>
              <SkipBack className="h-4 w-4" />
            </Button>

            {/* Frame back */}
            <Button variant="ghost" size="icon" onClick={prevFrame}>
              <ChevronLeft className="h-4 w-4" />
            </Button>

            {/* Frame forward */}
            <Button variant="ghost" size="icon" onClick={nextFrame}>
              <ChevronRight className="h-4 w-4" />
            </Button>

            {/* Skip forward */}
            <Button variant="ghost" size="icon" onClick={skipForward}>
              <SkipForward className="h-4 w-4" />
            </Button>

            {/* Time display */}
            <span className="text-sm text-muted-foreground ml-2">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {/* Speed selector */}
            <select
              value={playbackSpeed}
              onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
              className="bg-transparent text-sm border border-border rounded px-2 py-1"
            >
              <option value={0.25}>0.25x</option>
              <option value={0.5}>0.5x</option>
              <option value={1}>1x</option>
              <option value={1.5}>1.5x</option>
              <option value={2}>2x</option>
            </select>

            {/* Drawing toggle */}
            <Button
              variant={isDrawingMode ? "default" : "ghost"}
              size="icon"
              onClick={() => setIsDrawingMode(!isDrawingMode)}
            >
              <Pencil className="h-4 w-4" />
            </Button>

            {/* Fullscreen */}
            <Button variant="ghost" size="icon">
              <Maximize2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
