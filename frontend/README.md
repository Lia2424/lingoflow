# LingoFlow — Frontend

React + TypeScript application for the LingoFlow language immersion platform.

---

## Folder Structure

```
src/
├── app/
│   └── App.tsx              # QueryClientProvider, BrowserRouter, root layout
├── components/
│   ├── ui/                  # Primitive components: Button, Badge, Card, Input, Modal
│   └── layout/              # Navbar, Sidebar, PageShell — shared across features
├── features/                # Co-located feature modules
│   ├── auth/                # Login, Register, onboarding (Milestone 1)
│   ├── discovery/           # Feed, filters, content cards (Milestone 2)
│   ├── content/             # Detail page, media embed, AI panel (Milestone 2-3)
│   ├── vocabulary/          # Word list, status management (Milestone 4)
│   ├── immersion-plan/      # AI plan view and generation (Milestone 4)
│   └── quiz/                # Quiz UI and results (Milestone 5)
├── hooks/
│   └── useDebounce.ts       # Shared custom hooks
├── lib/
│   └── axios.ts             # Axios instance with auth interceptors
├── services/                # Typed API call functions (one file per domain)
│   ├── auth.ts
│   ├── content.ts
│   ├── vocabulary.ts
│   └── ai.ts
├── stores/
│   ├── authStore.ts         # Zustand — auth user + access token
│   └── preferencesStore.ts  # Zustand — discovery feed filters
├── types/
│   └── index.ts             # All global TypeScript interfaces and enums
└── utils/
    ├── cefr.ts              # CEFR labels, colors, level array
    └── format.ts            # Duration, content type, relative time formatters
```

### Module Boundaries

Each `features/<name>/` directory is a vertical slice. It owns its own:
- Components (feature-specific, not shared)
- Hooks (e.g. `useDiscoveryFeed`, `useContentDetail`)
- Types (if only relevant to that feature)

Nothing inside a feature is imported from another feature. Shared code lives in `components/`, `hooks/`, `services/`, `stores/`, `types/`, and `utils/`.

### Data Flow

```
Component
  └── useQuery / useInfiniteQuery (TanStack Query)
        └── services/content.ts          ← typed fetch function
              └── lib/axios.ts           ← configured Axios instance
                    └── /api/v1/...      ← FastAPI backend
```

Components never call `axios` directly. All API calls go through `services/`.
Global state (auth, preferences) lives in Zustand stores. Server state (content, vocab) is owned by TanStack Query.

---

## Local Development (without Docker)

### Prerequisites

- Node.js 20+
- Backend API running on `http://localhost:8000`

### Setup

```bash
cd frontend
npm install
npm run dev
```

App runs at http://localhost:5173. API requests to `/api/*` are proxied to `http://localhost:8000` (configured in `vite.config.ts`).

---

## Environment Variables

Vite exposes variables prefixed with `VITE_` to the browser bundle.

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Backend base URL (Docker only — local uses Vite proxy) |

Create a `.env.local` file in the `frontend/` directory to override defaults. Never commit real values.

---

## Available Scripts

| Script | Description |
|---|---|
| `npm run dev` | Start Vite dev server with HMR |
| `npm run build` | TypeScript compile + production bundle |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | ESLint on all `.ts` / `.tsx` files |
| `npm run type-check` | `tsc --noEmit` — type check without building |

---

## Key Patterns

### TanStack Query keys

Query keys follow the pattern `[domain, ...filters]` to enable precise cache invalidation:

```ts
// Discovery feed (paginated)
['content', { language, cefr, type, q }]

// Single content item
['content', contentId]

// User's vocabulary
['vocabulary', userId]
```

### Zustand stores

Stores use `persist` middleware for auth and preferences. Auth state is partialised — only `user` and `accessToken` are written to `localStorage`, not the full store.

### Path aliases

`@/` resolves to `src/` in both TypeScript and Vite:

```ts
import { useAuthStore } from '@/stores/authStore'
import type { ContentItem } from '@/types'
```

---

## CEFR Reference

| Level | Label | Tailwind color |
|---|---|---|
| A1 | Beginner | `bg-green-100 text-green-800` |
| A2 | Elementary | `bg-emerald-100 text-emerald-800` |
| B1 | Intermediate | `bg-blue-100 text-blue-800` |
| B2 | Upper Intermediate | `bg-indigo-100 text-indigo-800` |
| C1 | Advanced | `bg-purple-100 text-purple-800` |
| C2 | Mastery | `bg-rose-100 text-rose-800` |

Use `cefrColor(level)` from `@/utils/cefr` to apply consistently.
