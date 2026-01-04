/**
 * Utility Functions
 */
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge Tailwind classes with clsx
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format timestamp to mm:ss
 */
export function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, "0")}:${secs
    .toString()
    .padStart(2, "0")}`;
}

/**
 * Format timestamp with milliseconds
 */
export function formatTimeMs(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  const ms = Math.floor((seconds % 1) * 1000);
  return `${mins.toString().padStart(2, "0")}:${secs
    .toString()
    .padStart(2, "0")}.${ms.toString().padStart(3, "0")}`;
}

/**
 * Convert frame number to timestamp (assuming 25 FPS)
 */
export function frameToTimestamp(frame: number, fps: number = 25): number {
  return frame / fps;
}

/**
 * Convert timestamp to frame number
 */
export function timestampToFrame(timestamp: number, fps: number = 25): number {
  return Math.floor(timestamp * fps);
}

/**
 * Pitch dimensions (in meters)
 */
export const PITCH_DIMENSIONS = {
  length: 105,
  width: 68,
} as const;

/**
 * Convert pitch coordinates to SVG coordinates
 */
export function pitchToSvg(
  pitchX: number,
  pitchY: number,
  svgWidth: number,
  svgHeight: number
): { x: number; y: number } {
  const x = (pitchX / PITCH_DIMENSIONS.length) * svgWidth;
  const y = (pitchY / PITCH_DIMENSIONS.width) * svgHeight;
  return { x, y };
}

/**
 * Team colors
 */
export const TEAM_COLORS = {
  home: {
    primary: "#3b82f6", // Blue
    secondary: "#1d4ed8",
  },
  away: {
    primary: "#ef4444", // Red
    secondary: "#b91c1c",
  },
  ball: "#fbbf24", // Yellow
} as const;

/**
 * Phase labels for display
 */
export const PHASE_LABELS: Record<string, string> = {
  ORGANIZED_ATTACK: "Organized Attack",
  ORGANIZED_DEFENSE: "Organized Defense",
  TRANSITION_ATK_DEF: "Transition (Atk→Def)",
  TRANSITION_DEF_ATK: "Transition (Def→Atk)",
};

/**
 * Debounce function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

/**
 * Throttle function
 */
export function throttle<T extends (...args: unknown[]) => unknown>(
  fn: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}
