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
import { Button, Skeleton } from "@/components/ui";
import { cn } from "@/src/utils";

interface MetricsPanelProps {
  matchId: string;
  className?: string;
}

// Demo PPDA data
const generatePPDAData = () => {
  const data = [];
  for (let i = 0; i <= 90; i += 5) {
    data.push({
      minute: i,
      ppda: 8 + Math.random() * 6,
      homeControl: 45 + Math.random() * 20,
      awayControl: 35 + Math.random() * 20,
    });
  }
  return data;
};

// Demo physical data
const generatePhysicalData = () => {
  const data = [];
  for (let i = 0; i <= 90; i += 15) {
    data.push({
      minute: i,
      avgSpeed: 6 + Math.random() * 4,
      distance: 1500 + Math.random() * 500,
      sprints: Math.floor(5 + Math.random() * 10),
    });
  }
  return data;
};

// Demo player comparison data
const PLAYER_DATA = [
  { name: "Player 9", distance: 11.2, sprints: 28, topSpeed: 32.1 },
  { name: "Player 7", distance: 10.8, sprints: 32, topSpeed: 33.5 },
  { name: "Player 10", distance: 10.5, sprints: 18, topSpeed: 29.8 },
  { name: "Player 8", distance: 12.1, sprints: 22, topSpeed: 30.2 },
  { name: "Player 6", distance: 11.8, sprints: 15, topSpeed: 28.5 },
];

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

export function MetricsPanel({ matchId, className }: MetricsPanelProps) {
  const { selectedPeriod, setSelectedPeriod } = useMatchStore();
  const [selectedTab, setSelectedTab] = useState<
    "ppda" | "physical" | "players"
  >("ppda");

  // Generate demo data
  const ppdaData = useMemo(() => generatePPDAData(), []);
  const physicalData = useMemo(() => generatePhysicalData(), []);

  // Filter by period
  const filteredPPDAData = useMemo(() => {
    switch (selectedPeriod) {
      case "first_half":
        return ppdaData.filter((d) => d.minute <= 45);
      case "second_half":
        return ppdaData.filter((d) => d.minute > 45);
      default:
        return ppdaData;
    }
  }, [ppdaData, selectedPeriod]);

  const filteredPhysicalData = useMemo(() => {
    switch (selectedPeriod) {
      case "first_half":
        return physicalData.filter((d) => d.minute <= 45);
      case "second_half":
        return physicalData.filter((d) => d.minute > 45);
      default:
        return physicalData;
    }
  }, [physicalData, selectedPeriod]);

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
          {/* PPDA Chart */}
          <div>
            <h4 className="text-sm font-medium mb-2">PPDA Over Time</h4>
            <div className="h-40">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={filteredPPDAData}>
                  <defs>
                    <linearGradient
                      id="ppdaGradient"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
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
                <AreaChart data={filteredPPDAData}>
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
        </div>
      )}

      {selectedTab === "physical" && (
        <div className="space-y-6">
          {/* Speed & Distance Chart */}
          <div>
            <h4 className="text-sm font-medium mb-2">Speed & Distance</h4>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={filteredPhysicalData}>
                  <XAxis
                    dataKey="minute"
                    tick={{ fill: "#9ca3af", fontSize: 10 }}
                    tickFormatter={(v) => `${v}'`}
                  />
                  <YAxis
                    yAxisId="left"
                    tick={{ fill: "#9ca3af", fontSize: 10 }}
                    label={{
                      value: "Distance (m)",
                      angle: -90,
                      position: "insideLeft",
                      fill: "#9ca3af",
                      fontSize: 10,
                    }}
                  />
                  <YAxis
                    yAxisId="right"
                    orientation="right"
                    tick={{ fill: "#9ca3af", fontSize: 10 }}
                    label={{
                      value: "Speed (km/h)",
                      angle: 90,
                      position: "insideRight",
                      fill: "#9ca3af",
                      fontSize: 10,
                    }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Bar
                    yAxisId="left"
                    dataKey="distance"
                    name="Distance (m)"
                    fill="#8b5cf6"
                    opacity={0.7}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="avgSpeed"
                    name="Avg Speed"
                    stroke="#10b981"
                    strokeWidth={2}
                    dot={false}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Sprints Chart */}
          <div>
            <h4 className="text-sm font-medium mb-2">Sprints</h4>
            <div className="h-32">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={filteredPhysicalData}>
                  <XAxis
                    dataKey="minute"
                    tick={{ fill: "#9ca3af", fontSize: 10 }}
                    tickFormatter={(v) => `${v}'`}
                  />
                  <YAxis tick={{ fill: "#9ca3af", fontSize: 10 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="sprints" name="Sprints" fill="#f59e0b" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {selectedTab === "players" && (
        <div>
          <h4 className="text-sm font-medium mb-2">
            Player Comparison - Distance (km)
          </h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={PLAYER_DATA} layout="vertical">
                <XAxis type="number" tick={{ fill: "#9ca3af", fontSize: 10 }} />
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
        </div>
      )}
    </div>
  );
}
