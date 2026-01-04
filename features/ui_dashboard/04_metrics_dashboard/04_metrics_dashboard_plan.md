# Implementation Plan: Metrics Dashboard Component

> **Reference Spec:** [04_metrics_dashboard_spec.md](./04_metrics_dashboard_spec.md)

## Overview

Time-series charts and statistics for tactical metrics analysis. Displays PPDA, Pitch Control, Speed/Distance with filtering capabilities.

---

## Design Reference

Based on mockups:

- **Charts:** Dark theme with gradient fills
- **Layout:** Stacked charts with period filter
- **Interactions:** Hover tooltips, player selection
- **Colors:** Blue for home team, red for away

---

## Component Structure

```
components/metrics/
├── MetricsPanel.tsx         # Container with filters
├── PPDAChart.tsx            # PPDA time series
├── PitchControlChart.tsx    # Pitch control area chart
├── SpeedDistanceChart.tsx   # Combined speed/distance
├── PlayerComparisonChart.tsx # Bar chart for player comparison
├── PeriodFilter.tsx         # First/Second half filter
└── PlayerSelector.tsx       # Multi-select for players
```

---

## Implementation Steps

### 1. MetricsPanel Container

```tsx
interface MetricsPanelProps {
  matchId: string;
  className?: string;
}
```

- Fetch metrics data with `useMatchMetrics(matchId)`
- Period filter controls
- Responsive grid layout

### 2. PPDA Chart (Recharts)

```tsx
<ResponsiveContainer width="100%" height={200}>
  <AreaChart data={ppdaData}>
    <defs>
      <linearGradient id="ppdaGradient" x1="0" y1="0" x2="0" y2="1">
        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
      </linearGradient>
    </defs>
    <XAxis dataKey="minute" tick={{ fill: "#9ca3af" }} />
    <YAxis tick={{ fill: "#9ca3af" }} />
    <Tooltip content={<CustomTooltip />} />
    <Area
      type="monotone"
      dataKey="ppda"
      stroke="#3b82f6"
      fill="url(#ppdaGradient)"
    />
  </AreaChart>
</ResponsiveContainer>
```

- Data: PPDA values over time (from metrics endpoint)
- X-axis: Match minutes (0-90)
- Tooltip: Minute, PPDA value, interpretation

### 3. Pitch Control Chart

```tsx
<AreaChart data={pitchControlData}>
  <Area dataKey="home" stackId="1" stroke="#3b82f6" fill="#3b82f6" />
  <Area dataKey="away" stackId="1" stroke="#ef4444" fill="#ef4444" />
</AreaChart>
```

- Stacked area showing home vs away control
- Data normalized to 100%
- ReferenceLine at 50% mark

### 4. Speed/Distance Chart

Combined chart showing:

- Line: Average team speed over time
- Bars: Total distance at intervals

```tsx
<ComposedChart data={physicalData}>
  <Bar dataKey="distance" fill="#8b5cf6" />
  <Line dataKey="avgSpeed" stroke="#10b981" />
</ComposedChart>
```

### 5. Player Comparison

Horizontal bar chart for selected players:

```tsx
<BarChart data={playerData} layout="vertical">
  <XAxis type="number" />
  <YAxis dataKey="name" type="category" />
  <Bar dataKey="totalDistance" fill="#3b82f6" />
</BarChart>
```

- Multi-select up to 5 players
- Metrics: Distance, Sprints, Top Speed

### 6. Period Filter

```tsx
<div className="flex gap-2">
  <Button
    variant={period === "all" ? "default" : "outline"}
    onClick={() => setPeriod("all")}
  >
    Full Match
  </Button>
  <Button
    variant={period === "first_half" ? "default" : "outline"}
    onClick={() => setPeriod("first_half")}
  >
    1st Half
  </Button>
  <Button
    variant={period === "second_half" ? "default" : "outline"}
    onClick={() => setPeriod("second_half")}
  >
    2nd Half
  </Button>
</div>
```

---

## Data Transformation

```typescript
function filterByPeriod(data: MetricPoint[], period: Period) {
  switch (period) {
    case "first_half":
      return data.filter((d) => d.minute <= 45);
    case "second_half":
      return data.filter((d) => d.minute > 45);
    default:
      return data;
  }
}
```

---

## Verification

- [ ] Charts render with mock data
- [ ] Period filter updates all charts
- [ ] Player selection works (max 5)
- [ ] Tooltips display on hover
- [ ] Responsive on different screen sizes
- [ ] Loading states shown while fetching
