# LingoFlow

A modern full-stack language immersion platform that helps users discover authentic content — articles, podcasts, YouTube videos, music, and TV shows — matched to their CEFR proficiency level, with AI-assisted understanding and personalized immersion plans.

> Not a vocabulary drill app. Not a Duolingo clone. A discovery engine for real content.

---

## Architecture

```
LingoFlow/
├── frontend/          React + TypeScript + TanStack Query + Zustand + Tailwind CSS
├── backend/           FastAPI + PostgreSQL + SQLAlchemy (async) + Redis
├── docker-compose.yml Local dev stack (postgres, redis, backend, frontend)
└── .github/workflows/ CI (lint + test) and image build pipelines
```

### System Diagram

```
Browser
  └── React (TanStack Query, Zustand)
        │ HTTP/JSON
        ▼
  FastAPI  (/api/v1/*)
  ├── Auth Service       → PostgreSQL (users, refresh tokens)
  ├── Content Service    → PostgreSQL + Redis (feed cache)
  ├── AI Service         → OpenAI API + Redis (response cache)
  └── Recommendation     → PostgreSQL
```

### Key Engineering Decisions

| Decision | Why |
|---|---|
| Feature-based frontend modules | Co-location makes features deletable; no file-type archaeology |
| Repository pattern (backend) | Isolates all DB access; services are testable without SQLAlchemy |
| Page-based pagination | Simple to implement and debug; content catalog is append-only so page drift is acceptable |
| JSONB for AI output | Quiz/plan schema evolves; avoids premature column design |
| Async SQLAlchemy + asyncpg | FastAPI is fully async; blocking DB calls negate its benefits |
| Redis cache on AI endpoints | Avoid redundant LLM calls; 1-hour TTL per content item |
| Rotating refresh tokens | Sliding session with token rotation detects token theft |
| `INSERT … ON CONFLICT DO UPDATE` | Atomic upsert for interactions; avoids a separate read-then-write and the TOCTOU race it creates |
| `COALESCE` in upsert set-clause | Allows partial updates (status-only) without overwriting previously set fields like rating |

---

## Quick Start

### Prerequisites

- Docker and Docker Compose v2
- (Optional, for local dev without Docker) Python 3.11+, Node 20+

### 1. Clone and configure environment

```bash
git clone https://github.com/your-username/lingoflow.git
cd lingoflow
cp .env.example .env
```

Edit `.env` and set at minimum:
- `POSTGRES_PASSWORD` — any strong password
- `SECRET_KEY` — generate with `openssl rand -hex 32`
- `OPENAI_API_KEY` — required for AI features (Milestone 4+)

### 2. Start the full stack

```bash
docker compose up --build
```

| Service  | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/api/docs |
| Health check | http://localhost:8000/health |

### 3. Run database migrations

```bash
docker compose exec backend alembic upgrade head
```

---

## Development Roadmap

| Milestone | Scope | Status |
|---|---|---|
| 0 — Scaffolding | Architecture, folder structure, Docker, CI | ✅ Complete |
| 1 — Auth | JWT auth, user onboarding, protected routes | ✅ Complete |
| 2 — Content + Discovery | Feed, filters, horizontal rows, content detail, interaction tracking | ✅ Complete |
| 3 — Vocabulary & Flashcards | Word saving, SRS scheduling, flashcard review session | ✅ Complete |
| 4 — App Shell & User Profile | Global nav bar, user avatar, logout, settings page | 🚧 In progress |
| 5 — AI Integration | CEFR scoring, vocabulary extraction, sentence explanation | Pending |
| 6 — Recommendations | Personalized feed, immersion plans | Pending |
| 7 — Quizzes + Progress | AI quiz generation, stats dashboard | Pending |
| 8 — Production | Structured logging, Sentry, Nginx, rate limiting hardening | Pending |

### Seed sample data (Milestone 2+)

```bash
docker compose exec backend python scripts/seed_content.py
```

This loads 21 items covering all source types (article, podcast, YouTube, music, TV show), all CEFR levels, and multiple languages.

---

## Tech Stack

**Frontend**
- [React 18](https://react.dev/) + [TypeScript 5](https://www.typescriptlang.org/)
- [TanStack Query v5](https://tanstack.com/query) — server state, caching, infinite scroll
- [Zustand](https://zustand-demo.pmnd.rs/) — lightweight client state
- [Tailwind CSS v4](https://tailwindcss.com/) — utility-first styling
- [React Router v6](https://reactrouter.com/)
- [Vite v5](https://vitejs.dev/) — build tooling

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — async Python API framework
- [PostgreSQL 16](https://www.postgresql.org/) + [asyncpg](https://github.com/MagicStack/asyncpg)
- [SQLAlchemy 2 (async)](https://docs.sqlalchemy.org/en/20/) — ORM
- [Alembic](https://alembic.sqlalchemy.org/) — schema migrations
- [Redis 7](https://redis.io/) — response caching
- [OpenAI API](https://platform.openai.com/) — CEFR estimation, vocab extraction, quiz generation

**Infrastructure**
- [Docker](https://www.docker.com/) + Docker Compose
- [GitHub Actions](https://github.com/features/actions) — CI/CD

---

## Project Structure

```
frontend/   See frontend/README.md
backend/    See backend/README.md
```

---

## Contributing

This is a portfolio project. Issues and pull requests welcome.

```bash
# Install pre-commit hooks (runs ruff on every commit)
pip install pre-commit
pre-commit install
```
