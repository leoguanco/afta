"use client";

import { useState, useCallback, useRef } from "react";
import {
  Button,
  Input,
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  Label,
  Progress,
} from "@/components/ui";
import { Upload, X, FileVideo, Loader2, CheckCircle } from "lucide-react";
import { cn } from "@/src/utils";
import { apiClient } from "@/src/api";
import { ProcessingStatus } from "./ProcessingStatus";

interface VideoUploadModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onUploadComplete?: (result: { matchId: string; jobId: string }) => void;
}

type UploadState = "idle" | "uploading" | "processing" | "complete" | "error";

export function VideoUploadModal({
  open,
  onOpenChange,
  onUploadComplete,
}: VideoUploadModalProps) {
  // File state
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Form state
  const [homeTeam, setHomeTeam] = useState("Home");
  const [awayTeam, setAwayTeam] = useState("Away");
  const [date, setDate] = useState("");
  const [competition, setCompetition] = useState("");
  const [videoMode, setVideoMode] = useState<"full_match" | "highlights">(
    "full_match"
  );

  // Upload state
  const [uploadState, setUploadState] = useState<UploadState>("idle");
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    matchId?: string;
    jobId?: string;
  } | null>(null);

  // Handle file selection
  const handleFile = useCallback((selectedFile: File) => {
    if (!selectedFile.type.startsWith("video/")) {
      setError("Please select a video file");
      return;
    }
    setFile(selectedFile);
    setError(null);
  }, []);

  // Drag and drop handlers
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFile(e.dataTransfer.files[0]);
      }
    },
    [handleFile]
  );

  // Handle file input change
  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files[0]) {
        handleFile(e.target.files[0]);
      }
    },
    [handleFile]
  );

  // Upload the video
  const handleUpload = useCallback(async () => {
    if (!file) return;

    setUploadState("uploading");
    setProgress(0);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("home_team", homeTeam);
      formData.append("away_team", awayTeam);
      if (date) formData.append("date", date);
      if (competition) formData.append("competition", competition);
      formData.append("mode", videoMode);
      formData.append("auto_process", "true");

      // Upload with progress tracking
      const response = await apiClient.post("/video/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setProgress(percentCompleted);
          }
        },
      });

      setUploadState("processing");
      setResult({
        matchId: response.data.match_id || response.data.upload_id,
        jobId: response.data.job_id,
      });

      // Store job info in localStorage for match page to access
      if (response.data.match_id && response.data.job_id) {
        localStorage.setItem(
          `processing-job-${response.data.match_id}`,
          JSON.stringify({
            jobId: response.data.job_id,
            matchId: response.data.match_id,
            startedAt: Date.now(),
          })
        );
      }

      // Transition to complete after a short delay
      setTimeout(() => {
        setUploadState("complete");
        if (
          onUploadComplete &&
          response.data.match_id &&
          response.data.job_id
        ) {
          onUploadComplete({
            matchId: response.data.match_id,
            jobId: response.data.job_id,
          });
        }
      }, 1500);
    } catch (err: unknown) {
      setUploadState("error");
      const errorMessage =
        err instanceof Error
          ? err.message
          : (err as { response?: { data?: { message?: string } } })?.response
              ?.data?.message || "Upload failed";
      setError(errorMessage);
    }
  }, [
    file,
    homeTeam,
    awayTeam,
    date,
    competition,
    videoMode,
    onUploadComplete,
  ]);

  // Reset modal state
  const handleReset = useCallback(() => {
    setFile(null);
    setUploadState("idle");
    setProgress(0);
    setError(null);
    setResult(null);
    setHomeTeam("Home");
    setAwayTeam("Away");
    setDate("");
    setCompetition("");
    setVideoMode("full_match");
  }, []);

  // Handle close
  const handleClose = useCallback(() => {
    if (uploadState === "uploading") return; // Don't allow close during upload
    handleReset();
    onOpenChange(false);
  }, [uploadState, handleReset, onOpenChange]);

  // Format file size
  const formatSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024)
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Upload Match Video</DialogTitle>
          <DialogDescription>
            Upload a football match video for AI-powered tactical analysis
          </DialogDescription>
        </DialogHeader>

        {uploadState === "idle" && (
          <>
            {/* Drop zone */}
            <div
              className={cn(
                "border-2 border-dashed rounded-lg p-8 text-center transition-colors",
                dragActive
                  ? "border-primary bg-primary/10"
                  : file
                  ? "border-green-500 bg-green-500/10"
                  : "border-muted-foreground/25 hover:border-muted-foreground/50"
              )}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => inputRef.current?.click()}
            >
              <input
                ref={inputRef}
                type="file"
                accept="video/*"
                onChange={handleInputChange}
                className="hidden"
              />

              {file ? (
                <div className="flex flex-col items-center gap-2">
                  <FileVideo className="h-12 w-12 text-green-500" />
                  <p className="font-medium">{file.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatSize(file.size)}
                  </p>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      setFile(null);
                    }}
                  >
                    <X className="h-4 w-4 mr-1" />
                    Remove
                  </Button>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-2">
                  <Upload className="h-12 w-12 text-muted-foreground" />
                  <p className="font-medium">Drop video file here</p>
                  <p className="text-sm text-muted-foreground">
                    or click to browse
                  </p>
                  <p className="text-xs text-muted-foreground mt-2">
                    Supports MP4, MOV, AVI, MKV (max 2GB)
                  </p>
                </div>
              )}
            </div>

            {/* Match metadata form */}
            {file && (
              <div className="grid grid-cols-2 gap-4 mt-4">
                <div>
                  <Label htmlFor="homeTeam">Home Team</Label>
                  <Input
                    id="homeTeam"
                    value={homeTeam}
                    onChange={(e) => setHomeTeam(e.target.value)}
                    placeholder="Home team name"
                  />
                </div>
                <div>
                  <Label htmlFor="awayTeam">Away Team</Label>
                  <Input
                    id="awayTeam"
                    value={awayTeam}
                    onChange={(e) => setAwayTeam(e.target.value)}
                    placeholder="Away team name"
                  />
                </div>
                <div>
                  <Label htmlFor="date">Match Date</Label>
                  <Input
                    id="date"
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="competition">Competition</Label>
                  <Input
                    id="competition"
                    value={competition}
                    onChange={(e) => setCompetition(e.target.value)}
                    placeholder="League / Cup name"
                  />
                </div>
                <div className="col-span-2">
                  <Label>Video Type</Label>
                  <div className="flex gap-4 mt-2">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="videoMode"
                        value="full_match"
                        checked={videoMode === "full_match"}
                        onChange={() => setVideoMode("full_match")}
                        className="w-4 h-4 accent-primary"
                      />
                      <span className="text-sm">Full Match</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="videoMode"
                        value="highlights"
                        checked={videoMode === "highlights"}
                        onChange={() => setVideoMode("highlights")}
                        className="w-4 h-4 accent-primary"
                      />
                      <span className="text-sm">Highlights</span>
                    </label>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {videoMode === "full_match"
                      ? "Processes entire video for comprehensive analysis"
                      : "Optimized for shorter highlight clips"}
                  </p>
                </div>
              </div>
            )}

            {error && <p className="text-sm text-destructive mt-2">{error}</p>}
          </>
        )}

        {/* Uploading state */}
        {uploadState === "uploading" && (
          <div className="py-8 text-center">
            <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-primary" />
            <p className="font-medium mb-2">Uploading video...</p>
            <Progress value={progress} className="w-full mb-2" />
            <p className="text-sm text-muted-foreground">
              {progress}% complete
            </p>
          </div>
        )}

        {/* Processing state */}
        {uploadState === "processing" && (
          <div className="py-8 text-center">
            <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-primary" />
            <p className="font-medium mb-2">Starting analysis...</p>
            <p className="text-sm text-muted-foreground">
              Video uploaded successfully. Processing will run in the
              background.
            </p>
          </div>
        )}

        {/* Complete state - shows processing status */}
        {uploadState === "complete" && result?.jobId && (
          <div className="py-4">
            <div className="mb-4 text-center">
              <CheckCircle className="h-10 w-10 mx-auto mb-2 text-green-500" />
              <p className="font-medium">Upload Complete!</p>
            </div>
            <div className="bg-muted/50 rounded-lg p-4">
              <p className="text-sm font-medium mb-3">Processing Status</p>
              <ProcessingStatus
                jobId={result.jobId}
                matchId={result.matchId}
                onComplete={(matchId) => {
                  onUploadComplete?.({ matchId, jobId: result.jobId! });
                }}
              />
            </div>
          </div>
        )}

        {/* Error state */}
        {uploadState === "error" && (
          <div className="py-8 text-center">
            <X className="h-12 w-12 mx-auto mb-4 text-destructive" />
            <p className="font-medium mb-2">Upload Failed</p>
            <p className="text-sm text-destructive mb-4">{error}</p>
            <Button variant="outline" onClick={handleReset}>
              Try Again
            </Button>
          </div>
        )}

        <DialogFooter>
          {uploadState === "idle" && (
            <>
              <Button variant="outline" onClick={handleClose}>
                Cancel
              </Button>
              <Button onClick={handleUpload} disabled={!file}>
                <Upload className="h-4 w-4 mr-2" />
                Upload & Process
              </Button>
            </>
          )}
          {uploadState === "complete" && (
            <Button onClick={handleClose}>Done</Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
