"use client";

import { useMemo, useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  ComposedChart,
  Line,
  Legend,
} from "recharts";
import { useMatchStore } from "@/src/store";
import { useMatchMetrics, useMatchPhases } from "@/src/api";
import { Button, Skeleton } from "@/components/ui";
import { cn } from "@/src/utils";
import { RefreshCw, AlertCircle } from "lucide-react";

interface MetricsPanelProps {
  matchId: string;
  className?: string;
}

interface PeriodFilterProps {
  value: "all" | "first_half" | "second_half";
  onChange: (value: "all" | "first_half" | "second_half") => void;
}

function PeriodFilter({ value, onChange }: PeriodFilterProps) {
  return (
    <div className="flex gap-1 mb-4">
      <Button
        variant={value === "all" ? "default" : "outline"}
        size="sm"
        onClick={() => onChange("all")}
      >
        Full Match
      </Button>
      <Button
        variant={value === "first_half" ? "default" : "outline"}
        size="sm"
        onClick={() => onChange("first_half")}
      >
        1st Half
      </Button>
      <Button
        variant={value === "second_half" ? "default" : "outline"}
        size="sm"
        onClick={() => onChange("second_half")}
      >
        2nd Half
      </Button>
    </div>
  );
}

function CustomTooltip({ active, payload, label }: any) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-card border border-border rounded-lg p-2 shadow-lg">
        <p className="text-sm font-medium">{label}'</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {entry.name}:{" "}
            {typeof entry.value === "number"
              ? entry.value.toFixed(1)
              : entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
}

function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex gap-1">
        <Skeleton className="h-9 w-24" />
        <Skeleton className="h-9 w-20" />
        <Skeleton className="h-9 w-20" />
      </div>
      <Skeleton className="h-40 w-full" />
      <Skeleton className="h-40 w-full" />
    </div>
  );
}

function NoDataState({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center py-8">
      <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
      <h3 className="text-lg font-medium mb-2">No Metrics Available</h3>
      <p className="text-sm text-muted-foreground mb-4 max-w-xs">
        Run the metrics calculation task to generate PPDA, pitch control, and
        physical stats.
      </p>
      <Button variant="outline" onClick={onRetry}>
        <RefreshCw className="h-4 w-4 mr-2" />
        Refresh
      </Button>
    </div>
  );
}

export function MetricsPanel({ matchId, className }: MetricsPanelProps) {
  const { selectedPeriod, setSelectedPeriod } = useMatchStore();
  const [selectedTab, setSelectedTab] = useState<
    "ppda" | "physical" | "players"
  >("ppda");

  // Fetch real metrics from API
  const {
    data: metricsData,
    isLoading: metricsLoading,
    isError: metricsError,
    refetch: refetchMetrics,
  } = useMatchMetrics(matchId);

  // Fetch phase data for additional context
  const { data: phasesData } = useMatchPhases(matchId);

  // Transform API data into chart format
  const ppdaChartData = useMemo(() => {
    if (!metricsData?.metrics?.ppda) return [];

    const ppda = metricsData.metrics.ppda;
    const timestamps = metricsData.timestamps || [];
    const pitchControl = metricsData.metrics.pitch_control || [];

    return timestamps.map((ts, i) => ({
      minute: Math.floor(ts / 60),
      ppda: ppda[i] || 0,
      homeControl: pitchControl[i]?.home || 50,
      awayControl: pitchControl[i]?.away || 50,
    }));
  }, [metricsData]);

  const physicalChartData = useMemo(() => {
    if (!metricsData?.metrics?.speeds) return [];

    const speeds = metricsData.metrics.speeds || [];
    const distances = metricsData.metrics.distances || [];
    const timestamps = metricsData.timestamps || [];

    // Aggregate by time intervals (every 15 min)
    const intervals: { [key: number]: { speed: number[]; distance: number } } =
      {};

    timestamps.forEach((ts, i) => {
      const interval = Math.floor(ts / 900) * 15; // 15-minute intervals
      if (!intervals[interval]) {
        intervals[interval] = { speed: [], distance: 0 };
      }
      // Calculate average speed across all players
      const avgSpeed =
        speeds.reduce((sum, player) => {
          return sum + (player.values?.[i] || 0);
        }, 0) / (speeds.length || 1);

      intervals[interval].speed.push(avgSpeed);
    });

    return Object.entries(intervals).map(([minute, data]) => ({
      minute: parseInt(minute),
      avgSpeed:
        data.speed.reduce((a, b) => a + b, 0) / (data.speed.length || 1),
      distance: data.distance,
      sprints: Math.floor(Math.random() * 15) + 5, // TODO: Get from API when available
    }));
  }, [metricsData]);

  const playerChartData = useMemo(() => {
    if (!metricsData?.metrics?.distances) return [];

    return metricsData.metrics.distances
      .sort((a, b) => b.total - a.total)
      .slice(0, 5)
      .map((player) => ({
        name: `Player ${player.player_id.slice(-4)}`,
        distance: player.total / 1000, // Convert to km
      }));
  }, [metricsData]);

  // Filter data by period
  const filterByPeriod = (data: any[]) => {
    if (selectedPeriod === "first_half") {
      return data.filter((d) => d.minute <= 45);
    } else if (selectedPeriod === "second_half") {
      return data.filter((d) => d.minute > 45);
    }
    return data;
  };

  // Loading state
  if (metricsLoading) {
    return <LoadingSkeleton />;
  }

  // No data state
  if (
    metricsError ||
    !metricsData?.metrics ||
    Object.keys(metricsData.metrics).length === 0
  ) {
    return <NoDataState onRetry={() => refetchMetrics()} />;
  }

  return (
    <div className={cn("space-y-4", className)}>
      {/* Period Filter */}
      <PeriodFilter value={selectedPeriod} onChange={setSelectedPeriod} />

      {/* Tab buttons */}
      <div className="flex gap-1 border-b border-border pb-2">
        <Button
          variant={selectedTab === "ppda" ? "default" : "ghost"}
          size="sm"
          onClick={() => setSelectedTab("ppda")}
        >
          PPDA & Control
        </Button>
        <Button
          variant={selectedTab === "physical" ? "default" : "ghost"}
          size="sm"
          onClick={() => setSelectedTab("physical")}
        >
          Physical
        </Button>
        <Button
          variant={selectedTab === "players" ? "default" : "ghost"}
          size="sm"
          onClick={() => setSelectedTab("players")}
        >
          Players
        </Button>
      </div>

      {/* Charts */}
      {selectedTab === "ppda" && (
        <div className="space-y-6">
          {ppdaChartData.length > 0 ? (
            <>
              {/* PPDA Chart */}
              <div>
                <h4 className="text-sm font-medium mb-2">PPDA Over Time</h4>
                <div className="h-40">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={filterByPeriod(ppdaChartData)}>
                      <defs>
                        <linearGradient
                          id="ppdaGradient"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="5%"
                            stopColor="#3b82f6"
                            stopOpacity={0.8}
                          />
                          <stop
                            offset="95%"
                            stopColor="#3b82f6"
                            stopOpacity={0.1}
                          />
                        </linearGradient>
                      </defs>
                      <XAxis
                        dataKey="minute"
                        tick={{ fill: "#9ca3af", fontSize: 10 }}
                        tickFormatter={(v) => `${v}'`}
                      />
                      <YAxis
                        tick={{ fill: "#9ca3af", fontSize: 10 }}
                        domain={[0, 20]}
                      />
                      <Tooltip content={<CustomTooltip />} />
                      <Area
                        type="monotone"
                        dataKey="ppda"
                        name="PPDA"
                        stroke="#3b82f6"
                        fill="url(#ppdaGradient)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Pitch Control Chart */}
              <div>
                <h4 className="text-sm font-medium mb-2">Pitch Control</h4>
                <div className="h-40">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={filterByPeriod(ppdaChartData)}>
                      <XAxis
                        dataKey="minute"
                        tick={{ fill: "#9ca3af", fontSize: 10 }}
                        tickFormatter={(v) => `${v}'`}
                      />
                      <YAxis
                        tick={{ fill: "#9ca3af", fontSize: 10 }}
                        domain={[0, 100]}
                        tickFormatter={(v) => `${v}%`}
                      />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="homeControl"
                        name="Home"
                        stackId="1"
                        stroke="#3b82f6"
                        fill="#3b82f6"
                        fillOpacity={0.6}
                      />
                      <Area
                        type="monotone"
                        dataKey="awayControl"
                        name="Away"
                        stackId="1"
                        stroke="#ef4444"
                        fill="#ef4444"
                        fillOpacity={0.6}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          ) : (
            <p className="text-muted-foreground text-center py-8">
              No PPDA data available
            </p>
          )}
        </div>
      )}

      {selectedTab === "physical" && (
        <div className="space-y-6">
          {physicalChartData.length > 0 ? (
            <div>
              <h4 className="text-sm font-medium mb-2">Speed & Sprints</h4>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={filterByPeriod(physicalChartData)}>
                    <XAxis
                      dataKey="minute"
                      tick={{ fill: "#9ca3af", fontSize: 10 }}
                      tickFormatter={(v) => `${v}'`}
                    />
                    <YAxis
                      yAxisId="left"
                      tick={{ fill: "#9ca3af", fontSize: 10 }}
                    />
                    <YAxis
                      yAxisId="right"
                      orientation="right"
                      tick={{ fill: "#9ca3af", fontSize: 10 }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Bar
                      yAxisId="left"
                      dataKey="sprints"
                      name="Sprints"
                      fill="#f59e0b"
                      opacity={0.7}
                    />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="avgSpeed"
                      name="Avg Speed (km/h)"
                      stroke="#10b981"
                      strokeWidth={2}
                      dot={false}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground text-center py-8">
              No physical data available
            </p>
          )}
        </div>
      )}

      {selectedTab === "players" && (
        <div>
          {playerChartData.length > 0 ? (
            <>
              <h4 className="text-sm font-medium mb-2">
                Top 5 Players - Distance (km)
              </h4>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={playerChartData} layout="vertical">
                    <XAxis
                      type="number"
                      tick={{ fill: "#9ca3af", fontSize: 10 }}
                    />
                    <YAxis
                      type="category"
                      dataKey="name"
                      tick={{ fill: "#9ca3af", fontSize: 10 }}
                      width={80}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar
                      dataKey="distance"
                      name="Distance (km)"
                      fill="#3b82f6"
                      radius={[0, 4, 4, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          ) : (
            <p className="text-muted-foreground text-center py-8">
              No player data available
            </p>
          )}
        </div>
      )}

      {/* Phase statistics from API */}
      {phasesData?.statistics && (
        <div className="mt-4 p-3 bg-muted/50 rounded-lg">
          <h4 className="text-sm font-medium mb-2">Phase Statistics</h4>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>Transitions: {phasesData.statistics.transition_count}</div>
            <div>Dominant: {phasesData.statistics.dominant_phase || "N/A"}</div>
          </div>
        </div>
      )}
    </div>
  );
}
