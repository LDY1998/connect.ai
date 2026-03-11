# Phase 1: Scaffold + Initial Input

## Overview
The goal of this phase is to establish the foundational architecture of the application and implement the initial user flow: submitting a URL/DOI and navigating to the graph page.

## Objectives
1. **Frontend Setup**
   - Initialize a Next.js 14 project in the `frontend/` directory.
   - Configure Tailwind CSS.
   - Set up `shadcn/ui` with a dark theme as the default.
   - Create basic routing (`app/page.tsx` for Home, `app/graph/[paperId]/page.tsx` for Graph View).

2. **Backend Setup**
   - Initialize a FastAPI project in the `backend/` directory.
   - Set up Python environment (e.g., `venv`, `requirements.txt`).
   - Configure basic CORS so the Next.js frontend can communicate with the backend.
   - Set up environment variables handling.

3. **Shared Types & Data Contracts**
   - Define data models for paper metadata (e.g., `Paper`, `Author`, `Citation`).
   - Ensure consistency between Pydantic models (Backend) and TypeScript interfaces (Frontend).

4. **Paper Provider Integration (Backend)**
   - Create an abstract paper provider interface.
   - Implement an initial provider (e.g., Semantic Scholar or OpenAlex) to fetch basic paper metadata and resolve DOIs/URLs.

5. **API Development (Backend)**
   - Implement `POST /api/v1/resolve`: Accepts URL/DOI and returns normalized `paperId` or basic metadata.
   - Implement `GET /api/v1/paper/{paper_id}`: Fetches basic metadata for a given paper.

6. **UI Implementation (Frontend)**
   - Build the Home page (`/`) featuring a `UrlInput` component.
   - Implement form submission logic to hit the backend `/api/v1/resolve` endpoint.
   - Handle redirection to `/graph/[paperId]` upon successful resolution.
   - Build a placeholder Graph page (`/graph/[paperId]`) that simply displays the fetched metadata to verify the end-to-end flow.

## Definition of Done
- [x] Both Next.js and FastAPI servers run concurrently.
- [ ] A user can paste a valid Paper URL or DOI into the home page.
- [ ] The Next.js frontend successfully calls the FastAPI backend.
- [ ] The FastAPI backend resolves the paper ID using a paper provider.
- [ ] The user is successfully redirected to the `/graph/[paperId]` route.
- [ ] The placeholder graph page displays the resolved paper ID or basic metadata.