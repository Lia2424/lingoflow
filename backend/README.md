# LingoFlow — Backend

FastAPI service powering the LingoFlow language immersion platform.

---

## Folder Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app factory, middleware, router mount
│   ├── api/
│   │   └── v1/                 # Route handlers (one file per domain)
│   │       ├── __init__.py     # Aggregates all routers into api_router
│   │       ├── auth.py         # POST /auth/{register,login,refresh,logout}
│   │       ├── users.py        # GET/PATCH /users/me + stats
│   │       ├── content.py      # Discovery feed + interactions
│   │       ├── vocabulary.py   # User word tracking
│   │       ├── recommendations.py
│   │       └── ai.py           # CEFR, sentence explanation, quiz, immersion plan
│   ├── core/
│   │   ├── config.py           # Pydantic Settings (all config from env)
│   │   ├── security.py         # JWT encode/decode, bcrypt
│   │   └── dependencies.py     # Reusable Depends() factories (CurrentUserIdDep, etc.)
│   ├── db/
│   │   ├── base.py             # DeclarativeBase + shared mixins (UUID, timestamps)
│   │   ├── session.py          # Async engine + session factory + get_db()
│   │   └── migrations/         # Alembic env.py + version scripts
│   ├── models/                 # SQLAlchemy ORM models (added per milestone)
│   ├── schemas/                # Pydantic request/response schemas
│   ├── services/               # Business logic (no SQLAlchemy here)
│   ├── repositories/           # All DB access (one class per aggregate root)
│   └── utils/                  # Shared pure helpers
└── tests/
    ├── conftest.py             # Fixtures: test DB, HTTP client with DI overrides
    ├── unit/                   # Pure function tests (security, utils)
    └── integration/            # HTTP-level tests via ASGI transport
```

### Layer responsibilities

- **Routes** (`api/v1/`) — parse HTTP, validate input, call services, serialize output. No business logic.
- **Services** — orchestrate use cases, call repositories. No SQLAlchemy, no HTTP.
- **Repositories** — all SQLAlchemy queries. Accept `AsyncSession`, return ORM models.
- **Schemas** — Pydantic models for request bodies and response serialization.

---

## Local Development (without Docker)

### 1. Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) — `pip install uv`
- PostgreSQL 16 running locally
- Redis 7 running locally

### 2. Install dependencies

```bash
cd backend
uv pip install --system -e ".[dev]"
```

### 3. Configure environment

```bash
cp ../.env.example .env
# Edit .env — set DATABASE_URL, SECRET_KEY at minimum
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Start the development server

```bash
uvicorn app.main:app --reload --port 8000
```

API docs available at http://localhost:8000/api/docs

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | — | `postgresql+asyncpg://user:pass@host/db` |
| `SECRET_KEY` | Yes | — | JWT signing key (`openssl rand -hex 32`) |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis connection string |
| `ENVIRONMENT` | No | `development` | `development` or `production` |
| `DEBUG` | No | `false` | Enables SQLAlchemy query logging |
| `OPENAI_API_KEY` | No | — | Required for Milestone 3 AI features |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | OpenAI model for AI endpoints |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | JWT access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `30` | JWT refresh token lifetime |
| `CORS_ORIGINS` | No | `["http://localhost:5173"]` | Allowed CORS origins |

---

## Database Migrations

```bash
# Create a new migration after changing models/
alembic revision --autogenerate -m "add user table"

# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Show migration history
alembic history --verbose
```

**Important:** Before running `--autogenerate`, ensure all model files are imported in `app/db/migrations/env.py`. Uncomment each import as models are added.

---

## Running Tests

```bash
# All tests
pytest

# With coverage report
pytest --cov=app --cov-report=term-missing

# Only unit tests (no DB required)
pytest tests/unit/

# Only integration tests
pytest tests/integration/
```

Tests use a dedicated `lingoflow_test` database. The `conftest.py` overrides the `get_db` FastAPI dependency so integration tests never touch the development database.

---

## API Overview

All routes are prefixed with `/api/`.

| Method | Path | Description | Milestone |
|---|---|---|---|
| POST | `/auth/register` | Create account | 1 |
| POST | `/auth/login` | Authenticate | 1 |
| POST | `/auth/refresh` | Rotate refresh token | 1 |
| POST | `/auth/logout` | Invalidate token | 1 |
| GET | `/users/me` | My profile | 1 |
| PATCH | `/users/me` | Update profile | 1 |
| GET | `/users/me/stats` | Progress stats | 5 |
| GET | `/api/content` | Discovery feed | 2 |
| GET | `/api/content/{id}` | Content detail | 2 |
| POST | `/api/content/{id}/interact` | Save / mark read / like | 2 |
| GET | `/api/recommendations` | Personalized feed | 4 |
| GET | `/api/vocabulary` | User word list | 4 |
| POST | `/api/vocabulary` | Save a word | 4 |
| GET | `/api/vocabulary/content/{id}` | Vocab extracted from content | 3 |
| POST | `/api/explain` | Explain a sentence | 3 |
| POST | `/api/difficulty` | Estimate CEFR level | 3 |
| GET | `/api/quiz/{content_id}` | Fetch/generate quiz | 5 |
| GET | `/api/immersion/plan` | Current immersion plan | 4 |
| POST | `/api/immersion/plan/generate` | Trigger plan generation | 4 |

---

## Code Quality

```bash
# Lint (with auto-fix)
ruff check . --fix

# Format
ruff format .

# Type check
mypy app
```

Ruff and mypy run automatically in CI on every pull request.
