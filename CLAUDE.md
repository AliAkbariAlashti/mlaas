# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

MLaaS: a Django REST backend + React SPA where e-commerce operators upload CSV/Excel transaction files and run analytics (RFM segmentation, market basket, purchase propensity, sales anomaly detection) asynchronously via Celery. Ten products exist in the catalog; only four are wired to real engines — the rest are "coming soon" and route to a waitlist instead of an engine.

## Commands

### Backend (Django, from repo root)

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
python manage.py test                      # all tests
python manage.py test apps.analytics        # single app
python -m unittest ml_engines.tests         # ML engine tests directly (no Django)
```

Celery worker and beat (needed for analysis to actually run — the API only enqueues):

```bash
CELERY_BROKER_URL=redis://localhost:6379/0 CELERY_RESULT_BACKEND=redis://localhost:6379/1 celery -A mlaas worker -l info
CELERY_BROKER_URL=redis://localhost:6379/0 CELERY_RESULT_BACKEND=redis://localhost:6379/1 celery -A mlaas beat -l info
```

Without `POSTGRES_DB` set, Django falls back to SQLite (`db.sqlite3`) — fine for solo backend work, but Celery still needs a real Redis.

### Frontend (from `frontend/`)

```bash
npm install
npm run dev        # vite dev server on :5173, proxies /api and /media to :8000
npm run build       # tsc --noEmit, then vite build — this is the type-check step, there is no separate lint/typecheck script
```

### Full stack (Docker Compose)

```bash
docker compose up --build
```

Brings up Postgres, Redis, Django (`web`, :8000), Celery worker, Celery beat, and the Vite dev server (`frontend`, :5173) together. Swagger UI at `/api/docs/`, OpenAPI schema at `/api/schema/`, admin at `/admin/`.

```bash
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py test
```

### MVP auth shortcut

OTP is hardcoded to `123456` (120s expiry) in `apps.authentication.services.send_otp` — there's no real SMS gateway yet (marked `TODO` there).

## Architecture

**Request flow**: React SPA → Django REST API (JWT bearer auth) → enqueues project UUID onto Redis → Celery worker loads the project, calls into `ml_engines`, writes results back to Postgres and exports an Excel file to the shared `media` volume → SPA polls `/projects/{id}/status/` until `SUCCESS`/`FAILED`, then fetches the type-specific result endpoint.

**App boundaries** (`apps/`):
- `authentication` — phone/OTP-based `User` model (`AUTH_USER_MODEL = authentication.User`), JWT issuance, business-profile completion.
- `analytics` — `AnalysisService` (the dynamic product catalog, editable in Django Admin — required/optional mapping fields, active vs. private-beta state, live here, *not* hardcoded in the API or frontend), `Project` (one row per upload, snapshots `analysis_type` from its service on save), one-to-one typed result models (`RFMResult`, `BasketResult`, `MLResult` — shared by propensity and anomaly), `WaitlistLead`, and `cron.py`'s hourly purge of raw uploads older than 48h (metadata/results are kept forever).
- `website` — public blog + contact form endpoints, unauthenticated.
- `ml_engines` — pure Python/Pandas/scikit-learn/MLXtend, **no Django imports**. This is intentional: engines take dataframes + column-name mappings in, return `(summary_metrics, chart_data, output_df)` out. `apps/analytics/tasks.py` is the only adapter layer between Celery/Django and this package. When changing analysis logic, edit here, not in `tasks.py`.

**Why the catalog is dynamic**: the product list (10 services, 4 active) lives in the `AnalysisService` table, not in code, because staff toggle active/private-beta state and edit required mapping fields from Django Admin without a deploy. Frontend and API both read this catalog live — never hardcode service codes, names, or required fields into new frontend code; fetch `/api/v1/services/`.

**Credits & idempotency**: starting an analysis (`StartAnalysisView`) locks the user row in a transaction, checks credit balance (`402` if none), decrements one credit, then enqueues — all inside one transaction so a race can't double-spend a credit. A project can only be started once (`409` if not `PENDING`); a `FAILED` project cannot be retried, only re-uploaded.

**Frontend structure** (`frontend/src/`): `App.tsx` holds global context (lang `en`/`fa`, theme, auth user) and routes `/app/*` (protected `CustomerWorkspace`, dashboard) vs everything else (public `LandingPage`, site), both lazy-loaded. `api.ts` is the single fetch client — handles JWT attach, one-shot 401 refresh-and-retry, and typed request helpers; add new backend calls here rather than calling `fetch` directly in components. i18n is a single `lang` flag threaded through context (`localize(lang, enValue, faValue)`), not a library — `fa` flips `<html dir="rtl">` and swaps fonts.

## Working conventions

- The API contract is documented end-to-end in `docs/frontend-api-flow.md` (request/response shapes, UX behavior per step, error-status matrix) and `docs/backend-technical-flow.md` (module responsibilities, sequence/state diagrams). Check these before guessing at endpoint behavior — they're kept authoritative for this project.
- `docs/prd.md`, `docs/tech-doc.md`, and `docs/project-arch.md` are earlier/aspirational drafts (naming and some fields drift from the current code, e.g. project name "AI-Analytics", `ai_analytics/` paths) — prefer the two docs above and the actual code when they disagree.
- Keep `ml_engines` free of Django imports — it's tested and usable standalone via `python -m unittest ml_engines.tests`.
- A `frontend-design` skill (`skills/frontend.skill`) is available in this repo for deliberate, non-templated visual design work on the site — use it when doing UI/UX or landing-page design passes rather than defaulting to generic layouts.
