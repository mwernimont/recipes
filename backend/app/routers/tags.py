from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.recipe import TagResponse
from app.services.recipe_service import get_all_tags

router = APIRouter()


@router.get("/", response_model=list[TagResponse])
def list_tags(db: Session = Depends(get_db)):
    return get_all_tags(db)