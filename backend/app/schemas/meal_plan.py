from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MealPlanCreate(BaseModel):
    recipe_ids: list[int]


class GroceryListItemResponse(BaseModel):
    id: int
    name: str
    amount: Optional[float] = None
    unit: Optional[str] = None
    notes: Optional[str] = None
    is_checked: bool

    model_config = {"from_attributes": True}


class GroceryListItemUpdate(BaseModel):
    is_checked: bool


class MealPlanRecipeResponse(BaseModel):
    id: int
    recipe_id: Optional[int] = None
    recipe_title: str
    items: list[GroceryListItemResponse] = []

    model_config = {"from_attributes": True}


class MealPlanResponse(BaseModel):
    id: int
    status: str
    created_at: datetime
    ended_at: Optional[datetime] = None
    recipes: list[MealPlanRecipeResponse] = []

    model_config = {"from_attributes": True}
