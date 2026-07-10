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
| 2 — Content + Discovery | Feed, filters, content detail, interaction tracking | ✅ Complete |
| 3 — Vocabulary & Flashcards | Word saving, SRS scheduling, flashcard review session | ✅ Complete |
| 4 — App Shell & User Profile | Global nav bar, user menu, settings page, profile/password endpoints | ✅ Complete |
| 5 — AI & Content Ingestion | YouTube/podcast/article ingest, CEFR auto-classify, AI vocab suggest, comprehension quizzes, admin ingest API, security hardening (SSRF, rate limits, error sanitization) | ✅ Complete |
| 6 — Auth & Platform Hardening | httpOnly refresh cookies, token revocation, server-side quiz grading, scheduled ingest jobs | Pending |
| 7 — Recommendations & Immersion | Personalized feed, immersion plans | Pending |
| 8 — Production | Structured logging, Sentry, Nginx, observability, stats dashboard | Pending |

### Seed sample data

```bash
# Static demo catalog (no API keys)
docker compose exec backend python scripts/seed_content.py

# Bulk YouTube ingest — requires YOUTUBE_API_KEY (Milestone 5+)
docker compose exec backend python scripts/seed_from_youtube.py
```

The static seed loads 21 items across source types, CEFR levels, and languages. The YouTube script upserts real videos for all supported languages and is safe to re-run.

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
