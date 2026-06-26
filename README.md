# Recipe Vault

A personal recipe manager. Import recipes from any URL or add them manually, scale ingredients by serving size, and track your progress through cooking steps.

## Features

- **URL import** — paste a recipe link and it automatically pulls the title, description, times, ingredients, and steps via schema.org JSON-LD
- **Manual entry** — add recipes from scratch with a full editing form
- **Serving scaler** — adjust servings and all ingredient quantities scale proportionally, displayed as readable fractions (½, ¾, etc.)
- **Step completion** — tap through steps while cooking to mark them done
- **Tag filtering** — tag recipes and filter your library by tag
- **Image upload** — attach a photo to any recipe
- **PWA** — installable as a standalone app; recipe list and images are cached for offline browsing

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 20+

### Install dependencies

```bash
# Python backend
cd backend && pip install -r requirements.txt && cd ..

# Node (root dev tooling + frontend)
npm install
cd frontend && npm install && cd ..
```

### Set up the database

```bash
cd backend && alembic upgrade head && cd ..
```

### Run

```bash
npm run dev
```

This starts both the API (port 8000) and the Vite dev server (port 5173) in one terminal. The backend auto-reloads on file changes.

## Tech stack

| Layer | Technology |
|---|---|
| API | FastAPI + SQLAlchemy + SQLite |
| Migrations | Alembic |
| Frontend | Vue 3 + Pinia + Vue Router |
| Bundler | Vite + vite-plugin-pwa |
| HTTP client | httpx (scraping), fetch (frontend) |

## Configuration

| Environment variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./recipe_vault.db` | SQLAlchemy connection string |
| `VITE_API_URL` | `http://localhost:8000/api` | Backend base URL for the frontend |

Set these in `backend/.env` and `frontend/.env.local` respectively.
