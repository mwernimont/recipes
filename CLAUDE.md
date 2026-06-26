# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Recipe Vault is a personal recipe manager. The backend is a Python/FastAPI REST API backed by SQLite; the frontend is a Vue 3 SPA served by Vite. They run as separate processes in development.

## Development commands

### Backend (run from `backend/`)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload          # API at http://localhost:8000
alembic upgrade head                   # apply migrations
alembic revision --autogenerate -m "description"  # generate a migration
```

### Frontend (run from `frontend/`)

```bash
npm install
npm run dev       # dev server at http://localhost:5173
npm run build     # production build
npm run lint      # oxlint + eslint (auto-fix)
npm run format    # prettier
```

## Architecture

### Backend (`backend/app/`)

Layered: **routers → services → SQLAlchemy ORM → SQLite**.

- `main.py` — FastAPI app, CORS (allows `localhost:5173` and `localhost:4173`), static file mount for `/uploads/`
- `database.py` — SQLAlchemy engine + `get_db()` dependency; `DATABASE_URL` env var defaults to `sqlite:///./recipe_vault.db`
- `models/recipe.py` — ORM models: `Recipe`, `Ingredient`, `Step`, `Tag`, many-to-many `recipe_tag`
- `schemas/recipe.py` — Pydantic v2 schemas for request/response; the public field names are `prep_time_minutes`, `cook_time_minutes`, and `order` (on steps) — not abbreviated forms
- `services/recipe_service.py` — all DB logic; tags are always lowercased and deduplicated via `get_or_create_tag()`
- `services/scraper_service.py` — fetches a URL with httpx, parses schema.org JSON-LD (`@type: Recipe`) to extract recipe data
- `routers/` — thin; delegates to services, maps HTTP errors

`RecipeUpdate` only patches the core scalar fields (title, description, source URL, times, servings). Ingredients, steps, and tags are set at create time only.

Uploaded images are saved to `uploads/` (relative to the process working directory) and stored in the DB as `/uploads/{uuid}.ext` — the leading slash and prefix are already in the stored value.

### Frontend (`frontend/src/`)

**Views → Pinia store → `services/api.js` → backend.**

- `stores/recipes.js` — single Pinia store; holds `recipes[]`, `currentRecipe`, `tags[]`, search/filter state, and all async actions
- `services/api.js` — thin fetch wrapper; the `request()` function merges headers as `{ 'Content-Type': 'application/json', ...options.headers }` then spreads `...options`, so passing `headers: {}` in options suppresses Content-Type (used for multipart image upload)
- `router/index.js` — three routes: `/` (LibraryView), `/recipe/:id` (RecipeDetailView), `/add` (AddRecipeView)
- `views/AddRecipeView.vue` — three-stage flow: `input` → `preview` → `done`; scraping and manual entry both funnel into `RecipePreviewForm`
- `components/RecipePreviewForm.vue` — editable form for new recipes; emits `save` with the full recipe payload

### Key field-name conventions (easy to confuse)

| Concept | Correct name | Wrong (don't use) |
|---|---|---|
| Prep time | `prep_time_minutes` | `prep_time` |
| Cook time | `cook_time_minutes` | `cook_time` |
| Step ordering | `order` | `step_number` |
| Image URL | `image_path` (already `/uploads/…`) | add `/uploads/` prefix again |

### PWA

`vite-plugin-pwa` generates a service worker. `NetworkFirst` caches `/api/recipes`, `CacheFirst` caches `/uploads/` images (30-day TTL). Icons live in `frontend/public/icons/`.

## Planned features

### Edit recipe system
The user wants to build a full edit recipe flow. Currently `RecipeUpdate` only patches scalar fields (title, description, source URL, times, servings) — ingredients, steps, and tags cannot be modified after creation. The edit system should allow updating all fields including ingredients, steps, and tags.

### Database migrations

Alembic is configured in `backend/alembic.ini`. The env reads all models via `app.models.recipe.Base.metadata` for autogenerate support. Run Alembic from the `backend/` directory so relative paths resolve correctly.
