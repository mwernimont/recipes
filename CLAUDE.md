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
- `models/meal_plan.py` — `MealPlan`, `MealPlanRecipe`, `GroceryListItem` (see "Weekly meal planner" below); ingredients are snapshotted onto `GroceryListItem` at plan-creation time rather than referencing live `Ingredient` rows, so an archived list survives later edits or deletion of the source recipe
- `services/meal_plan_service.py` — enforces one active (not yet `completed`/`cancelled`) plan at a time; `create_meal_plan` does the ingredient snapshotting
- `routers/meal_plans.py` — mounted at `/api/meal-plans`; the static `/active` route must be declared before the `/{meal_plan_id}` path-param route, or FastAPI/Starlette matches "active" against the int param first and 422s instead of falling through
- `routers/` — thin; delegates to services, maps HTTP errors

`RecipeUpdate` patches the core scalar fields (title, description, source URL, times, servings) plus optional `ingredients`, `steps`, `tags` — when a collection field is included in the PATCH body it fully replaces the existing collection (empty list clears it); when omitted, that collection is left untouched.

Uploaded images are saved to `uploads/` (relative to the process working directory) and stored in the DB as `/uploads/{uuid}.ext` — the leading slash and prefix are already in the stored value.

### Frontend (`frontend/src/`)

**Views → Pinia store → `services/api.js` → backend.**

- `stores/recipes.js` — single Pinia store for the recipe library; holds `recipes[]`, `currentRecipe`, search state, and all async actions
- `stores/mealPlan.js` — separate Pinia store scoped to the *active* meal plan only (`activeMealPlan`, plus fetch/create/check-item/delete-item/complete/cancel actions). Archive browsing doesn't go through this store — `ArchiveView.vue`/`ArchiveDetailView.vue` fetch directly via `services/api.js` into local component state instead, since that data is read-only and page-local, same reasoning as `MealPlanView.vue`'s own state below
- `services/api.js` — thin fetch wrapper; the `request()` function merges headers as `{ 'Content-Type': 'application/json', ...options.headers }` then spreads `...options`, so passing `headers: {}` in options suppresses Content-Type (used for multipart image upload). Thrown errors carry a `.status` property so callers can distinguish, e.g., a 404 meaning "nothing there yet" from a real failure
- `router/index.js` — routes: `/` (LibraryView), `/recipe/:id` (RecipeDetailView), `/recipe/:id/edit` (EditRecipeView), `/add` (AddRecipeView), `/meal-plan` (MealPlanView), `/grocery-list` (GroceryListView), `/archive` (ArchiveView), `/archive/:id` (ArchiveDetailView)
- `views/AddRecipeView.vue` — three-stage flow: `input` → `preview` → `done`; scraping and manual entry both funnel into `RecipePreviewForm`
- `views/EditRecipeView.vue` — fetches an existing recipe and feeds it into `RecipePreviewForm`; on save, PATCHes via `store.updateRecipe()` and returns to the detail view
- `components/RecipePreviewForm.vue` — editable form shared by create and edit flows; emits `save` with the full recipe payload. Accepts optional `heading`/`submitLabel` props so the two flows can use different copy, and an `error` prop so the caller can surface a failed save inline
- `views/MealPlanView.vue` — meal plan builder (see "Weekly meal planner" below); all its state (meal count, accepted list, suggestion batch, deny cooldown, search) is local component state, not in the Pinia store, since it's ephemeral and single-view. `onMounted` checks `mealPlanStore` for an already-active plan and redirects straight to `/grocery-list` if one exists, rather than letting you build a redundant second plan
- `components/MealPlanCard.vue` — recipe card used by `MealPlanView`; a `variant` prop (`'suggestion'` | `'accepted'`) switches the footer between accept/deny controls and a remove button. Not the same component as `RecipeCard.vue`, whose root is a `RouterLink` that always navigates and so can't host action buttons
- `views/GroceryListView.vue` (`/grocery-list`) — the active plan's grocery list, gated on an active plan existing (falls back to fetching one on refresh, redirects to `/meal-plan` if there truly isn't one). "Mark Complete" / "Cancel Plan" call the corresponding backend endpoint and clear the store's active plan
- `components/GroceryListSection.vue` — renders one recipe's worth of grocery items (checkbox, amount/unit/name, delete button); a `readonly` prop disables the checkboxes and drops the delete button, shared between `GroceryListView.vue` and the read-only `ArchiveDetailView.vue` so the two can't drift apart
- `views/ArchiveView.vue` / `ArchiveDetailView.vue` — list of past (completed/cancelled) plans and a read-only detail view of one, both fetched straight from the API rather than through a store (see `stores/mealPlan.js` note above)
- `utils/formatAmount.js` — fraction-formatting for ingredient amounts (`0.5` → `½`), extracted out of `RecipeDetailView.vue` when the grocery list views needed the same formatting
- `utils/capitalize.js` — capitalizes a status string for display; used instead of CSS `text-transform: capitalize` on the archive status pills after that CSS property was observed to silently fail to render in one of the two places it was used, for reasons that didn't reproduce in isolation

### Styling

Component `<style>` blocks use `lang="scss"`. `frontend/src/styles/_variables.scss` (colors, spacing, radii, shadows) and `_mixins.scss` (`button-variant`, `card`, `tag-pill`, `outline-button`, `state-message`) are auto-injected into every component via `vite.config.js`'s `css.preprocessorOptions.scss.additionalData` — don't add `@use` imports for them in individual components. Prefer an existing variable/mixin over a new hardcoded value; if a needed shade doesn't exist, add it to `_variables.scss` rather than hardcoding, and never reach for `!important` — fix selector specificity instead (e.g. nest with `&` under the more specific parent rule).

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
The user wants a planner that assigns recipes from the library to days of the week, built incrementally in slices.

**Slice 1 — done** (`MealPlanView.vue` + `MealPlanCard.vue`, reachable via the "Meal Plan" nav link): pick a meal count (1–7), then build a set of that many accepted recipes by either searching the library by title or requesting random suggestions (`Help me plan` / `Show me more recipes`) that you accept or deny per card. Denying doesn't reshuffle immediately — it just marks the card; clicking the batch button puts marked cards on a 3-pull cooldown (tracked in a local `Map<recipeId, pullsRemaining>`) and fully refreshes the suggestion batch for whatever slots are still open. Everything is client-side/ephemeral — no backend model or persistence yet, since `store.recipes` already holds the full library.

**Slice 2 — done** (grocery list + archive, backed by real persistence — `models/meal_plan.py`, `routers/meal_plans.py`, `stores/mealPlan.js`, `GroceryListView.vue`, `ArchiveView.vue`, `ArchiveDetailView.vue`): once the accepted set hits the target count, "Accept Plan →" POSTs to `/api/meal-plans`, which snapshots each accepted recipe's title and ingredients rather than referencing them live (see the `models/meal_plan.py` note above). Only one plan can be active at a time — starting a new one 409s until the current one is completed or cancelled. The grocery list groups items by recipe with a checkbox and delete button per item, both persisted immediately; "Mark Complete" / "Cancel Plan" move the plan to a terminal status, after which it shows up in the archive. Quantities are shown exactly as saved on the recipe — no servings scaling in this slice.

**Still planned, not yet scoped for implementation:**
- Assign the accepted recipes to specific days (calendar/grid view), rather than stopping at an unordered set.
- Scale grocery list quantities to a chosen servings target, reusing the scaling logic already in `RecipeDetailView.vue` (the fraction-formatting half of that logic now lives in `utils/formatAmount.js`, shared with the grocery list; the scaling-by-ratio math itself hasn't been extracted or reused yet).
- Reuse or copy a past (archived) plan to start a new one, rather than only viewing it read-only.
- Tag-based suggestion filtering/avoidance (e.g. excluding desserts) — raised during design but explicitly cut from slice 1.

### Database migrations

Alembic is configured in `backend/alembic.ini`. `env.py` imports `app.models.recipe` for `Base.metadata`, plus an explicit `from app.models import meal_plan` so those tables register on the same metadata too — `env.py` doesn't scan `app/models/` automatically, so any future new model module needs the same explicit import added there or autogenerate won't see it. Run Alembic from the `backend/` directory so relative paths resolve correctly.
