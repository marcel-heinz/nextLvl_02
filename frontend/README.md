Next.js app with a scalable MVP skeleton for an E2E insurance automation platform.

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

Key pages live under `src/app/(app)/*` with a consistent app shell.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) with [Geist](https://vercel.com/font).

## App Structure

- `src/app/(app)/layout.tsx`: App shell with `Sidebar` and `Topbar`.
- `src/app/(app)/page.tsx`: Dashboard.
- `src/app/(app)/pipeline/page.tsx`: Kanban pipeline with CRUD via FastAPI.
- `src/components/ui/*`: Small UI primitives.
- `src/components/pipeline/*`: Pipeline components.
- `src/lib/api.ts`: API client, proxied via `next.config.ts` to backend.
- `src/lib/types.ts`: Shared types.

Teal palette per PRD: `#008B8B`, `#20B2AA`, `#AFEEEE`.
