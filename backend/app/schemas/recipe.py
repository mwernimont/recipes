from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


# --- Ingredient Schemas ---

class IngredientBase(BaseModel):
    name: str
    amount: Optional[float] = None
    unit: Optional[str] = None
    notes: Optional[str] = None


class IngredientCreate(IngredientBase):
    pass


class IngredientResponse(IngredientBase):
    id: int
    recipe_id: int

    model_config = {"from_attributes": True}


# --- Step Schemas ---

class StepBase(BaseModel):
    order: int
    instruction: str


class StepCreate(StepBase):
    pass


class StepResponse(StepBase):
    id: int
    recipe_id: int

    model_config = {"from_attributes": True}


# --- Tag Schemas ---

class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int

    model_config = {"from_attributes": True}


# --- Recipe Schemas ---

class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    source_url: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: float = 4.0


class RecipeCreate(RecipeBase):
    ingredients: list[IngredientCreate] = []
    steps: list[StepCreate] = []
    tags: list[str] = []


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: Optional[float] = None


class RecipeResponse(RecipeBase):
    id: int
    image_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    ingredients: list[IngredientResponse] = []
    steps: list[StepResponse] = []
    tags: list[TagResponse] = []

    model_config = {"from_attributes": True}


class RecipeListResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image_path: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: float
    tags: list[TagResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Scraper Schemas ---

class ScrapeRequest(BaseModel):
    url: str


class ScrapeResponse(BaseModel):
    title: str
    description: Optional[str] = None
    source_url: str
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: Optional[float] = None
    ingredients: list[IngredientCreate] = []
    steps: list[StepCreate] = []