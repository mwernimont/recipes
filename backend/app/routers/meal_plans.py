from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.meal_plan import (
    GroceryListItemResponse, GroceryListItemUpdate,
    MealPlanCreate, MealPlanResponse,
)
from app.services import meal_plan_service

router = APIRouter()


@router.post("/", response_model=MealPlanResponse, status_code=201)
def create_meal_plan(data: MealPlanCreate, db: Session = Depends(get_db)):
    try:
        return meal_plan_service.create_meal_plan(db, data)
    except meal_plan_service.ActiveMealPlanExistsError:
        raise HTTPException(status_code=409, detail="An active meal plan already exists")
    except meal_plan_service.RecipesNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Recipes not found: {e.missing_ids}")


@router.get("/active", response_model=MealPlanResponse)
def get_active_meal_plan(db: Session = Depends(get_db)):
    meal_plan = meal_plan_service.get_active_meal_plan(db)
    if not meal_plan:
        raise HTTPException(status_code=404, detail="No active meal plan")
    return meal_plan


@router.get("/{meal_plan_id}", response_model=MealPlanResponse)
def get_meal_plan(meal_plan_id: int, db: Session = Depends(get_db)):
    meal_plan = meal_plan_service.get_meal_plan(db, meal_plan_id)
    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return meal_plan


@router.get("/", response_model=list[MealPlanResponse])
def list_meal_plans(status: str | None = Query(None), db: Session = Depends(get_db)):
    return meal_plan_service.get_meal_plans(db, status=status)


@router.post("/{meal_plan_id}/complete", response_model=MealPlanResponse)
def complete_meal_plan(meal_plan_id: int, db: Session = Depends(get_db)):
    try:
        meal_plan = meal_plan_service.end_meal_plan(db, meal_plan_id, status="completed")
    except ValueError:
        raise HTTPException(status_code=409, detail="Meal plan is not active")
    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return meal_plan


@router.post("/{meal_plan_id}/cancel", response_model=MealPlanResponse)
def cancel_meal_plan(meal_plan_id: int, db: Session = Depends(get_db)):
    try:
        meal_plan = meal_plan_service.end_meal_plan(db, meal_plan_id, status="cancelled")
    except ValueError:
        raise HTTPException(status_code=409, detail="Meal plan is not active")
    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return meal_plan


@router.patch("/items/{item_id}", response_model=GroceryListItemResponse)
def update_item(item_id: int, data: GroceryListItemUpdate, db: Session = Depends(get_db)):
    item = meal_plan_service.set_item_checked(db, item_id, data.is_checked)
    if not item:
        raise HTTPException(status_code=404, detail="Grocery list item not found")
    return item


@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    deleted = meal_plan_service.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Grocery list item not found")
