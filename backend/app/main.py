from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routers import recipes, scraper, tags, meal_plans

app = FastAPI(
    title="Recipe Vault",
    description="Personal recipe manager API",
    version="0.1.0",
)

# CORS - allow Vue dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:4173",  # Vite preview
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploaded images
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
app.include_router(recipes.router, prefix="/api/recipes", tags=["recipes"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["scraper"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(meal_plans.router, prefix="/api/meal-plans", tags=["meal-plans"])


@app.get("/api/health")
def health_check():
    return {"status": "ok"}