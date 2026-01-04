/**
 * API Client - TanStack Query Hooks
 *
 * Axios client and React Query hooks for data fetching.
 */
import axios from "axios";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

// =============================================================================
// Axios Instance
// =============================================================================

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add correlation ID to requests
apiClient.interceptors.request.use((config) => {
  config.headers["X-Correlation-ID"] = crypto.randomUUID().slice(0, 8);
  return config;
});

// =============================================================================
// Types
// =============================================================================

export interface Match {
  match_id: string;
  home_team_id: string;
  away_team_id: string;
  event_count: number;
}

export interface MatchMetrics {
  match_id: string;
  metrics: {
    ppda: number[];
    pitch_control: number[];
    speeds: { player_id: string; values: number[] }[];
    distances: { player_id: string; total: number }[];
  };
  timestamps: number[];
}

export interface TrackingFrame {
  frame_id: number;
  timestamp: number;
  players: {
    player_id: string;
    team: "home" | "away";
    x: number;
    y: number;
    jersey_number?: number;
  }[];
  ball?: { x: number; y: number };
}

export interface PhaseData {
  match_id: string;
  team_id: string;
  status: string;
  phases: {
    frame_id: number;
    phase: string;
    confidence: number;
  }[];
  statistics: {
    transition_count: number;
    phase_percentages: Record<string, number>;
    dominant_phase?: string;
  };
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

// =============================================================================
// Query Hooks
// =============================================================================

/**
 * Fetch match details
 */
export function useMatch(matchId: string | null) {
  return useQuery({
    queryKey: ["match", matchId],
    queryFn: async () => {
      if (!matchId) return null;
      const { data } = await apiClient.get<Match>(`/matches/${matchId}`);
      return data;
    },
    enabled: !!matchId,
  });
}

/**
 * Fetch match metrics
 */
export function useMatchMetrics(matchId: string | null) {
  return useQuery({
    queryKey: ["metrics", matchId],
    queryFn: async () => {
      if (!matchId) return null;
      // Note: Backend returns job_id, we'd need to poll.
      // For now, check if we have stored metrics
      const { data } = await apiClient.get<MatchMetrics>(
        `/matches/${matchId}/metrics`
      );
      return data;
    },
    enabled: !!matchId,
    retry: false,
  });
}

/**
 * Fetch phase classification data
 */
export function useMatchPhases(
  matchId: string | null,
  teamId: string = "home"
) {
  return useQuery({
    queryKey: ["phases", matchId, teamId],
    queryFn: async () => {
      if (!matchId) return null;
      const { data } = await apiClient.get<PhaseData>(
        `/matches/${matchId}/phases`,
        {
          params: { team_id: teamId },
        }
      );
      return data;
    },
    enabled: !!matchId,
  });
}

/**
 * Fetch tracking data for a frame range
 */
export function useTrackingData(
  matchId: string | null,
  startFrame?: number,
  endFrame?: number
) {
  return useQuery({
    queryKey: ["tracking", matchId, startFrame, endFrame],
    queryFn: async () => {
      if (!matchId) return null;
      const { data } = await apiClient.get<TrackingFrame[]>(
        `/matches/${matchId}/tracking`,
        {
          params: { start_frame: startFrame, end_frame: endFrame },
        }
      );
      return data;
    },
    enabled: !!matchId,
  });
}

// =============================================================================
// Mutation Hooks
// =============================================================================

interface AnalyzeRequest {
  match_id: string;
  query: string;
}

/**
 * Start AI analysis (returns EventSource for SSE)
 */
export function useAnalyze() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: AnalyzeRequest) => {
      // POST triggers SSE stream
      const response = await fetch(`${API_BASE_URL}/chat/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error("Analysis request failed");
      }

      return response;
    },
  });
}

/**
 * Process a video file
 */
export function useProcessVideo() {
  return useMutation({
    mutationFn: async (request: {
      video_path: string;
      output_path: string;
      metadata?: {
        home_team: string;
        away_team: string;
        date?: string;
        competition?: string;
      };
      mode?: "full_match" | "highlights";
    }) => {
      const { data } = await apiClient.post("/process-video", request);
      return data;
    },
  });
}

/**
 * Poll job status
 */
export function useJobStatus(jobId: string | null) {
  return useQuery({
    queryKey: ["job", jobId],
    queryFn: async () => {
      if (!jobId) return null;
      const { data } = await apiClient.get(`/chat/jobs/${jobId}`);
      return data;
    },
    enabled: !!jobId,
    refetchInterval: (data) => {
      // Stop polling when completed or failed
      if (data?.status === "COMPLETED" || data?.status === "FAILED") {
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
  });
}
