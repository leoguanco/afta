# Implementation Plan: Dashboard Infrastructure

> **Reference Spec:** [01_dashboard_infrastructure_spec.md](./01_dashboard_infrastructure_spec.md)

## Overview

Foundation layer for the analyst dashboard. Establishes project structure, state management, API client, and design system.

---

## Design Reference

Based on provided mockups:

- **Theme:** Dark mode with glassmorphism effects
- **Colors:** Blue accents (#3b82f6), neutral grays (#1f2937 → #111827)
- **Typography:** Inter font family, clean hierarchy
- **Layout:** 4-panel grid with resizable sections

---

## File Structure

```
frontend/
├── app/
│   ├── globals.css          # Design tokens, dark theme
│   ├── layout.tsx           # Root layout with providers
│   ├── page.tsx             # Match listing home
│   ├── providers.tsx        # QueryClient + theme providers
│   └── matches/
│       └── [id]/
│           └── page.tsx     # Match detail dashboard
├── src/
│   ├── store.ts             # Zustand global state
│   ├── api.ts               # Axios + TanStack Query
│   └── utils.ts             # Helpers
└── components/
    └── ui/                   # Base components
        ├── Button.tsx
        ├── Card.tsx
        ├── Input.tsx
        ├── Select.tsx
        ├── ScrollArea.tsx
        ├── Skeleton.tsx
        └── Toast.tsx
```

---

## Implementation Steps

### 1. Providers Setup

- Create `QueryClientProvider` wrapper
- Configure default query options (staleTime, retry)
- Add dark mode class to html element

### 2. Global CSS / Design Tokens

```css
:root {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --card: 222.2 84% 6%;
  --primary: 217.2 91.2% 59.8%;
  --accent: 217.2 32.6% 17.5%;
  --border: 217.2 32.6% 17.5%;
}
```

### 3. Base UI Components

Implement minimal Shadcn-style components:

- `Button` - variants: default, outline, ghost
- `Card` - glassmorphism container
- `Input` - text input with label
- `Select` - dropdown with options
- `ScrollArea` - custom scrollbar
- `Skeleton` - loading placeholder
- `Toast` - notifications

### 4. Zustand Store

Already created at `src/store.ts` with:

- Match context (matchId)
- Video sync (currentFrame, currentTimestamp)
- Visualization toggles
- Period filter

### 5. API Client

Already created at `src/api.ts` with:

- Axios instance
- Query hooks for matches, metrics, phases, tracking
- Mutation hooks for analyze, processVideo

---

## Verification

- [ ] `npm run dev` starts without errors
- [ ] Dark mode renders correctly
- [ ] API client connects to backend
- [ ] Store state updates reactively
