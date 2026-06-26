from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.recipe import RecipeCreate, RecipeUpdate, RecipeResponse, RecipeListResponse
from app.services import recipe_service
import shutil
import uuid
import os

router = APIRouter()


@router.get("/", response_model=list[RecipeListResponse])
def list_recipes(
    search: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return recipe_service.get_recipes(db, search=search, tag=tag, skip=skip, limit=limit)


@router.post("/", response_model=RecipeResponse, status_code=201)
def create_recipe(data: RecipeCreate, db: Session = Depends(get_db)):
    return recipe_service.create_recipe(db, data)


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = recipe_service.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.patch("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(recipe_id: int, data: RecipeUpdate, db: Session = Depends(get_db)):
    recipe = recipe_service.update_recipe(db, recipe_id, data)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    deleted = recipe_service.delete_recipe(db, recipe_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Recipe not found")


@router.post("/{recipe_id}/image", response_model=RecipeResponse)
def upload_image(
    recipe_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content_type_ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
    if file.content_type not in content_type_ext:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WebP images are allowed")

    ext = content_type_ext[file.content_type]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join("uploads", filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    recipe = recipe_service.update_recipe_image(db, recipe_id, f"/uploads/{filename}")
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe