import { useMemo, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useTrackingData, TrackingFrame } from "../api";

// Chunk size for data fetching (500 frames @ 25fps = 20 seconds of data)
const CHUNK_SIZE = 500;

/**
 * Hook to buffer tracking data fetching.
 *
 * Instead of fetching frame-by-frame, this fetches data in chunks
 * and serves the specific frame from the cached chunk.
 *
 * @param matchId The match ID
 * @param currentFrame The current frame number
 */
export function useTrackingBuffer(matchId: string, currentFrame: number) {
  const queryClient = useQueryClient();

  // Calculate which chunk we need
  // e.g. frame 1050 -> chunk start 1000, end 1500
  const chunkStart = Math.floor(currentFrame / CHUNK_SIZE) * CHUNK_SIZE;
  const chunkEnd = chunkStart + CHUNK_SIZE;

  // Fetch the current chunk
  // React Query will handle deduplication and caching automatically
  const {
    data: chunkData,
    isLoading,
    isError,
    refetch,
  } = useTrackingData(matchId, chunkStart, chunkEnd);

  // Pre-fetch the NEXT chunk if we are in the second half of the buffer
  // This ensures seamless playback
  useEffect(() => {
    if (!matchId) return;

    const relativePosition = currentFrame - chunkStart;
    const shouldPrefetch = relativePosition > CHUNK_SIZE * 0.7; // Prefetch when 70% through

    if (shouldPrefetch) {
      const nextChunkStart = chunkEnd;
      const nextChunkEnd = nextChunkStart + CHUNK_SIZE;

      // Use queryClient to prefetch
      // We must match the queryKey used in useTrackingData: ["tracking", matchId, start, end]
      queryClient.prefetchQuery({
        queryKey: ["tracking", matchId, nextChunkStart, nextChunkEnd],
        queryFn: async () => {
          // We can't reuse the fetcher from api.ts easily without exporting it alone,
          // so we rely on calling the hook indirectly or just trusting the cache mechanism
          // actually prefetchQuery needs the fetcher.
          // Let's rely on the fact that if useTrackingData is called with these params later,
          // it will be fresh.

          // Better approach: Just let specific cached query handle it.
          // Implementation detail: we need the fetch function here.
          // Let's import apiClient and do it.
          const { apiClient } = await import("../api");
          const { data } = await apiClient.get<TrackingFrame[]>(
            `/matches/${matchId}/tracking`,
            {
              params: { start_frame: nextChunkStart, end_frame: nextChunkEnd },
            }
          );
          return data;
        },
        staleTime: 60 * 1000, // 1 minute
      });
    }
  }, [matchId, currentFrame, chunkStart, chunkEnd, queryClient]);

  // Extract the specific frame data from the chunk
  const frameData = useMemo(() => {
    if (!chunkData) return null;

    // Find the exact frame
    // Optimization: The API returns a list. We can use .find()
    // Since list is sorted and ~500 items, .find() is fast enough.
    return chunkData.find((f) => f.frame_id === currentFrame);
  }, [chunkData, currentFrame]);

  return {
    frameData,
    isLoading,
    isError,
    refetch,
    bufferedRange: { start: chunkStart, end: chunkEnd }, // For debug/display
  };
}
