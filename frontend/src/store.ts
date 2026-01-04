/**
 * Global State Store - Zustand
 *
 * Manages shared state for video/pitch synchronization and match context.
 */
import { create } from "zustand";

interface MatchStore {
  // Match Context
  matchId: string | null;

  // Video/Pitch Synchronization
  currentFrame: number;
  currentTimestamp: number;
  isPlaying: boolean;
  playbackSpeed: number;

  // Visualization Layers
  showPlayerDots: boolean;
  showHeatmap: boolean;
  showVoronoi: boolean;

  // Period Filter
  selectedPeriod: "all" | "first_half" | "second_half";

  // Actions
  setMatchId: (id: string | null) => void;
  setCurrentFrame: (frame: number) => void;
  setCurrentTimestamp: (timestamp: number) => void;
  setIsPlaying: (playing: boolean) => void;
  setPlaybackSpeed: (speed: number) => void;
  togglePlayerDots: () => void;
  toggleHeatmap: () => void;
  toggleVoronoi: () => void;
  setSelectedPeriod: (period: "all" | "first_half" | "second_half") => void;
  reset: () => void;
}

const initialState = {
  matchId: null,
  currentFrame: 0,
  currentTimestamp: 0,
  isPlaying: false,
  playbackSpeed: 1,
  showPlayerDots: true,
  showHeatmap: false,
  showVoronoi: false,
  selectedPeriod: "all" as const,
};

export const useMatchStore = create<MatchStore>((set) => ({
  ...initialState,

  setMatchId: (id) => set({ matchId: id }),
  setCurrentFrame: (frame) => set({ currentFrame: frame }),
  setCurrentTimestamp: (timestamp) => set({ currentTimestamp: timestamp }),
  setIsPlaying: (playing) => set({ isPlaying: playing }),
  setPlaybackSpeed: (speed) => set({ playbackSpeed: speed }),
  togglePlayerDots: () =>
    set((state) => ({ showPlayerDots: !state.showPlayerDots })),
  toggleHeatmap: () => set((state) => ({ showHeatmap: !state.showHeatmap })),
  toggleVoronoi: () => set((state) => ({ showVoronoi: !state.showVoronoi })),
  setSelectedPeriod: (period) => set({ selectedPeriod: period }),
  reset: () => set(initialState),
}));
