"use client";

import { useState, useEffect, useCallback } from "react";
import { Progress, Button } from "@/components/ui";
import {
  CheckCircle,
  Loader2,
  XCircle,
  Clock,
  Play,
  RefreshCw,
} from "lucide-react";
import { cn } from "@/src/utils";
import { apiClient } from "@/src/api";

interface ProcessingStatusProps {
  jobId: string;
  matchId?: string;
  onComplete?: (matchId: string) => void;
  onError?: (error: string) => void;
  className?: string;
}

type JobStatus =
  | "queued"
  | "processing"
  | "completed"
  | "failed"
  | "cancelled"
  | "unknown";

interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  state: string;
  progress?: number;
  message?: string;
  match_id?: string;
  error?: string;
}

export function ProcessingStatus({
  jobId,
  matchId,
  onComplete,
  onError,
  className,
}: ProcessingStatusProps) {
  const [status, setStatus] = useState<JobStatusResponse | null>(null);
  const [polling, setPolling] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const { data } = await apiClient.get<JobStatusResponse>(
        `/video/job/${jobId}`
      );
      setStatus(data);

      if (data.status === "completed") {
        setPolling(false);
        if (onComplete && (data.match_id || matchId)) {
          onComplete(data.match_id || matchId!);
        }
      } else if (data.status === "failed") {
        setPolling(false);
        setError(data.error || "Processing failed");
        if (onError) {
          onError(data.error || "Processing failed");
        }
      } else if (data.status === "cancelled") {
        setPolling(false);
      }
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : "Failed to fetch status";
      setError(errorMsg);
      setPolling(false);
    }
  }, [jobId, matchId, onComplete, onError]);

  // Poll for status updates
  useEffect(() => {
    if (!polling) return;

    fetchStatus();
    const interval = setInterval(fetchStatus, 3000); // Poll every 3 seconds

    return () => clearInterval(interval);
  }, [polling, fetchStatus]);

  const getStatusIcon = () => {
    switch (status?.status) {
      case "queued":
        return (
          <Clock className="h-5 w-5 text-muted-foreground animate-pulse" />
        );
      case "processing":
        return <Loader2 className="h-5 w-5 text-primary animate-spin" />;
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "failed":
        return <XCircle className="h-5 w-5 text-destructive" />;
      case "cancelled":
        return <XCircle className="h-5 w-5 text-muted-foreground" />;
      default:
        return (
          <Loader2 className="h-5 w-5 text-muted-foreground animate-spin" />
        );
    }
  };

  const getStatusColor = () => {
    switch (status?.status) {
      case "completed":
        return "text-green-500";
      case "failed":
        return "text-destructive";
      case "processing":
        return "text-primary";
      default:
        return "text-muted-foreground";
    }
  };

  if (!status && !error) {
    return (
      <div className={cn("flex items-center gap-2", className)}>
        <Loader2 className="h-4 w-4 animate-spin" />
        <span className="text-sm text-muted-foreground">Loading status...</span>
      </div>
    );
  }

  return (
    <div className={cn("space-y-3", className)}>
      {/* Status header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <span className={cn("font-medium capitalize", getStatusColor())}>
            {status?.status || "Unknown"}
          </span>
        </div>
        {status?.status === "processing" && status.progress !== undefined && (
          <span className="text-sm text-muted-foreground">
            {status.progress}%
          </span>
        )}
      </div>

      {/* Progress bar (for processing state) */}
      {status?.status === "processing" && (
        <Progress value={status.progress || 0} className="h-2" />
      )}

      {/* Status message */}
      <p className="text-sm text-muted-foreground">
        {status?.message || error || "Processing..."}
      </p>

      {/* Error details */}
      {status?.status === "failed" && status.error && (
        <p className="text-xs text-destructive/80 bg-destructive/10 p-2 rounded">
          {status.error}
        </p>
      )}

      {/* Action buttons */}
      <div className="flex gap-2">
        {status?.status === "completed" && (status.match_id || matchId) && (
          <Button size="sm" asChild>
            <a href={`/matches/${status.match_id || matchId}`}>
              <Play className="h-4 w-4 mr-1" />
              View Analysis
            </a>
          </Button>
        )}
        {(status?.status === "failed" || error) && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setError(null);
              setPolling(true);
            }}
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            Retry Check
          </Button>
        )}
      </div>
    </div>
  );
}
