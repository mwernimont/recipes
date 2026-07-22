from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.recipe import Recipe, Ingredient, Step, Tag
from app.schemas.recipe import RecipeCreate, RecipeUpdate


def get_or_create_tag(db: Session, name: str) -> Tag:
    tag = db.query(Tag).filter(Tag.name == name.lower().strip()).first()
    if not tag:
        tag = Tag(name=name.lower().strip())
        db.add(tag)
        db.flush()
    return tag


def create_recipe(db: Session, data: RecipeCreate) -> Recipe:
    recipe = Recipe(
        title=data.title,
        description=data.description,
        source_url=data.source_url,
        prep_time_minutes=data.prep_time_minutes,
        cook_time_minutes=data.cook_time_minutes,
        servings=data.servings,
    )
    db.add(recipe)
    db.flush()  # get recipe.id before adding children

    for ing in data.ingredients:
        db.add(Ingredient(
            recipe_id=recipe.id,
            name=ing.name,
            amount=ing.amount,
            unit=ing.unit,
            notes=ing.notes,
        ))

    for step in data.steps:
        db.add(Step(
            recipe_id=recipe.id,
            order=step.order,
            instruction=step.instruction,
        ))

    for tag_name in data.tags:
        tag = get_or_create_tag(db, tag_name)
        recipe.tags.append(tag)

    db.commit()
    db.refresh(recipe)
    return recipe


def get_recipe(db: Session, recipe_id: int) -> Recipe | None:
    return db.query(Recipe).filter(Recipe.id == recipe_id).first()


def get_recipes(
    db: Session,
    search: str | None = None,
    tag: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Recipe]:
    query = db.query(Recipe)

    if search:
        query = query.filter(
            or_(
                Recipe.title.ilike(f"%{search}%"),
                Recipe.description.ilike(f"%{search}%"),
            )
        )

    if tag:
        query = query.join(Recipe.tags).filter(Tag.name == tag.lower().strip())

    return query.order_by(Recipe.created_at.desc()).offset(skip).limit(limit).all()


def update_recipe(db: Session, recipe_id: int, data: RecipeUpdate) -> Recipe | None:
    recipe = get_recipe(db, recipe_id)
    if not recipe:
        return None

    update_data = data.model_dump(exclude_unset=True)

    ingredients_data = update_data.pop("ingredients", None)
    steps_data = update_data.pop("steps", None)
    tags_data = update_data.pop("tags", None)

    for field, value in update_data.items():
        setattr(recipe, field, value)

    if ingredients_data is not None:
        recipe.ingredients = [
            Ingredient(
                name=ing["name"], amount=ing["amount"],
                unit=ing["unit"], notes=ing["notes"],
            )
            for ing in ingredients_data
        ]

    if steps_data is not None:
        recipe.steps = [
            Step(order=step["order"], instruction=step["instruction"])
            for step in steps_data
        ]

    if tags_data is not None:
        recipe.tags = [get_or_create_tag(db, tag_name) for tag_name in tags_data]

    db.commit()
    db.refresh(recipe)
    return recipe


def delete_recipe(db: Session, recipe_id: int) -> bool:
    recipe = get_recipe(db, recipe_id)
    if not recipe:
        return False
    db.delete(recipe)
    db.commit()
    return True


def update_recipe_image(db: Session, recipe_id: int, image_path: str) -> Recipe | None:
    recipe = get_recipe(db, recipe_id)
    if not recipe:
        return None
    recipe.image_path = image_path
    db.commit()
    db.refresh(recipe)
    return recipe


def get_all_tags(db: Session) -> list[Tag]:
    return db.query(Tag).filter(Tag.recipes.any()).order_by(Tag.name).all()