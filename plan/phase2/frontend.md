# Phase 2: Frontend Goals

## Overview
Implement the interactive citation graph using React Flow. The frontend will fetch the pre-computed graph layout from the backend and render it using custom nodes and edges.

## Objectives

### 1. Dependencies
Install the following packages in `frontend/`:

```bash
npm install @xyflow/react zustand d3-scale d3-color
npm install -D @types/d3-scale @types/d3-color
```

---

### 2. TypeScript Types
Create `frontend/types/graph.ts` mirroring the backend graph models:

```ts
import type { Paper } from "./paper";

export interface NodePosition {
  x: number;
  y: number;
}

export interface GraphNodeData extends Paper {}

export interface GraphNode {
  id: string;
  position: NodePosition;
  data: GraphNodeData;
  type: string;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  seedPaperId: string;
}
```

---

### 3. Zustand Store
Create `frontend/store/graphStore.ts`:

```ts
import { create } from "zustand";
import type { GraphData } from "@/types/graph";

interface GraphStore {
  graphData: GraphData | null;
  selectedPaperId: string | null;
  setGraphData: (data: GraphData) => void;
  setSelectedPaperId: (id: string | null) => void;
}

export const useGraphStore = create<GraphStore>((set) => ({
  graphData: null,
  selectedPaperId: null,
  setGraphData: (data) => set({ graphData: data }),
  setSelectedPaperId: (id) => set({ selectedPaperId: id }),
}));
```

---

### 4. Graph Components

#### `frontend/components/graph/GraphCanvas.tsx`
- `"use client"` component wrapping `<ReactFlow>` from `@xyflow/react`.
- Receives `GraphData` as a prop.
- Registers custom node and edge types (`PaperNode`, `CitationEdge`).
- On node click, calls `useGraphStore.setSelectedPaperId`.
- Includes `<Background>`, `<Controls>`, and `<MiniMap>`.

#### `frontend/components/graph/PaperNode.tsx`
- Custom React Flow node component.
- Displays: truncated paper title, year badge, citation count ring.
- Seed node gets a glowing/pulsing ring to distinguish it.
- Color of the node determined by publication year using a `d3-scale` gradient.

#### `frontend/components/graph/CitationEdge.tsx`
- Custom React Flow edge component.
- Directional animated arrow using React Flow's `BaseEdge` + `EdgeLabelRenderer`.
- Fades non-hovered edges when any edge is hovered.

#### `frontend/components/graph/GraphToolbar.tsx`
- Floating toolbar in the top-left corner.
- Buttons: Fit view, Zoom in, Zoom out.
- Uses React Flow's `useReactFlow()` hook.

#### `frontend/components/graph/GraphLegend.tsx`
- Fixed bottom-left overlay.
- Shows the year gradient bar from oldest to newest year in the graph.

---

### 5. Wire Up Graph Page
Update `frontend/app/graph/[paperId]/page.tsx`:

- Keep the server component structure.
- Fetch graph data from `POST /api/v1/graph` instead of the paper detail endpoint.
- Pass `GraphData` to a new `"use client"` wrapper component that renders `GraphCanvas`.
- Remove the Phase 2 placeholder.

---

## Definition of Done
- [ ] Graph page renders an interactive React Flow canvas instead of the placeholder.
- [ ] Seed paper is visually distinct (glowing ring) at the center.
- [ ] Surrounding papers are colored by publication year.
- [ ] Clicking a node sets `selectedPaperId` in the Zustand store (console.log to verify).
- [ ] Fit view, zoom in, zoom out toolbar buttons work.
- [ ] Year gradient legend is visible.