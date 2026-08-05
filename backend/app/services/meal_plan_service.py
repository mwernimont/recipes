from datetime import datetime
from sqlalchemy.orm import Session
from app.models.recipe import Recipe
from app.models.meal_plan import MealPlan, MealPlanRecipe, GroceryListItem
from app.schemas.meal_plan import MealPlanCreate


class ActiveMealPlanExistsError(Exception):
    pass


class RecipesNotFoundError(Exception):
    def __init__(self, missing_ids: list[int]):
        self.missing_ids = missing_ids
        super().__init__(f"Recipes not found: {missing_ids}")


def get_active_meal_plan(db: Session) -> MealPlan | None:
    return (
        db.query(MealPlan)
        .filter(MealPlan.status == "active")
        .order_by(MealPlan.created_at.desc())
        .first()
    )


def get_meal_plan(db: Session, meal_plan_id: int) -> MealPlan | None:
    return db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()


def get_meal_plans(db: Session, status: str | None = None) -> list[MealPlan]:
    query = db.query(MealPlan)
    if status:
        query = query.filter(MealPlan.status == status)
    return query.order_by(MealPlan.created_at.desc()).all()


def create_meal_plan(db: Session, data: MealPlanCreate) -> MealPlan:
    if get_active_meal_plan(db) is not None:
        raise ActiveMealPlanExistsError()

    recipes = db.query(Recipe).filter(Recipe.id.in_(data.recipe_ids)).all()
    recipes_by_id = {r.id: r for r in recipes}
    missing_ids = [rid for rid in data.recipe_ids if rid not in recipes_by_id]
    if missing_ids:
        raise RecipesNotFoundError(missing_ids)

    meal_plan = MealPlan(status="active")
    db.add(meal_plan)
    db.flush()  # get meal_plan.id

    for recipe_id in data.recipe_ids:
        recipe = recipes_by_id[recipe_id]
        plan_recipe = MealPlanRecipe(
            meal_plan_id=meal_plan.id,
            recipe_id=recipe.id,
            recipe_title=recipe.title,
        )
        db.add(plan_recipe)
        db.flush()  # get plan_recipe.id

        for ing in recipe.ingredients:
            db.add(GroceryListItem(
                meal_plan_recipe_id=plan_recipe.id,
                name=ing.name,
                amount=ing.amount,
                unit=ing.unit,
                notes=ing.notes,
            ))

    db.commit()
    db.refresh(meal_plan)
    return meal_plan


def set_item_checked(db: Session, item_id: int, is_checked: bool) -> GroceryListItem | None:
    item = db.query(GroceryListItem).filter(GroceryListItem.id == item_id).first()
    if not item:
        return None
    item.is_checked = is_checked
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item_id: int) -> bool:
    item = db.query(GroceryListItem).filter(GroceryListItem.id == item_id).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def delete_meal_plan(db: Session, meal_plan_id: int) -> bool:
    meal_plan = get_meal_plan(db, meal_plan_id)
    if not meal_plan:
        return False
    if meal_plan.status == "active":
        raise ValueError("Cannot delete an active meal plan")
    db.delete(meal_plan)
    db.commit()
    return True


def end_meal_plan(db: Session, meal_plan_id: int, status: str) -> MealPlan | None:
    """Move an active plan to a terminal status ('completed' or 'cancelled')."""
    meal_plan = get_meal_plan(db, meal_plan_id)
    if not meal_plan:
        return None
    if meal_plan.status != "active":
        raise ValueError("Meal plan is not active")
    meal_plan.status = status
    meal_plan.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(meal_plan)
    return meal_plan
