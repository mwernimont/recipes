from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(20), nullable=False, default="active")  # active | completed | cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    recipes = relationship(
        "MealPlanRecipe", back_populates="meal_plan",
        cascade="all, delete-orphan", order_by="MealPlanRecipe.id",
    )


class MealPlanRecipe(Base):
    __tablename__ = "meal_plan_recipes"

    id = Column(Integer, primary_key=True, index=True)
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id"), nullable=False)
    # Nullable + a snapshot title: the source recipe may be edited or deleted
    # later, and an archived plan should still read fine either way.
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=True)
    recipe_title = Column(String(255), nullable=False)

    meal_plan = relationship("MealPlan", back_populates="recipes")
    recipe = relationship("Recipe")
    items = relationship(
        "GroceryListItem", back_populates="meal_plan_recipe",
        cascade="all, delete-orphan", order_by="GroceryListItem.id",
    )


class GroceryListItem(Base):
    __tablename__ = "grocery_list_items"

    id = Column(Integer, primary_key=True, index=True)
    meal_plan_recipe_id = Column(Integer, ForeignKey("meal_plan_recipes.id"), nullable=False)
    name = Column(String(255), nullable=False)
    amount = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    notes = Column(String(255), nullable=True)
    is_checked = Column(Boolean, nullable=False, default=False)

    meal_plan_recipe = relationship("MealPlanRecipe", back_populates="items")
