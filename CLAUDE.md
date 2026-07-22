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

`RecipeUpdate` patches the core scalar fields (title, description, source URL, times, servings) plus optional `ingredients`, `steps`, `tags` — when a collection field is included in the PATCH body it fully replaces the existing collection (empty list clears it); when omitted, that collection is left untouched.

Uploaded images are saved to `uploads/` (relative to the process working directory) and stored in the DB as `/uploads/{uuid}.ext` — the leading slash and prefix are already in the stored value.

### Frontend (`frontend/src/`)

**Views → Pinia store → `services/api.js` → backend.**

- `stores/recipes.js` — single Pinia store; holds `recipes[]`, `currentRecipe`, `tags[]`, search/filter state, and all async actions
- `services/api.js` — thin fetch wrapper; the `request()` function merges headers as `{ 'Content-Type': 'application/json', ...options.headers }` then spreads `...options`, so passing `headers: {}` in options suppresses Content-Type (used for multipart image upload)
- `router/index.js` — four routes: `/` (LibraryView), `/recipe/:id` (RecipeDetailView), `/recipe/:id/edit` (EditRecipeView), `/add` (AddRecipeView)
- `views/AddRecipeView.vue` — three-stage flow: `input` → `preview` → `done`; scraping and manual entry both funnel into `RecipePreviewForm`
- `views/EditRecipeView.vue` — fetches an existing recipe and feeds it into `RecipePreviewForm`; on save, PATCHes via `store.updateRecipe()` and returns to the detail view
- `components/RecipePreviewForm.vue` — editable form shared by create and edit flows; emits `save` with the full recipe payload. Accepts optional `heading`/`submitLabel` props so the two flows can use different copy

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

### Weekly meal planner
The user wants a planner that assigns recipes from the library to days of the week. Scope as discussed:
- Assign recipes to days (calendar/grid view over the library, not just a flat list).
- Auto-generate a shopping list by aggregating ingredients across the week's planned recipes, respecting each recipe's servings scaling (see the scaling logic already in `RecipeDetailView.vue`).
- Persist plans so they can be reused/copied across weeks, rather than being ephemeral client-only state (implies new backend models/endpoints, not just frontend state).
- Iterative regeneration with accept/deny per slot: the user can accept or deny individual recipe assignments; regenerating the plan only swaps out denied slots for new suggestions and leaves accepted ones locked in place. The recipe-selection/suggestion algorithm for what fills a slot (random, tag-based, avoid-recent-repeats, etc.) is still an open design question to resolve when this is scoped for implementation.

### Database migrations

Alembic is configured in `backend/alembic.ini`. The env reads all models via `app.models.recipe.Base.metadata` for autogenerate support. Run Alembic from the `backend/` directory so relative paths resolve correctly.
