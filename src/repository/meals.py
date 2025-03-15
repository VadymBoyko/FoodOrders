from uuid import UUID

from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from src.config.messages import DUPLICATE_MEAL_NAME
from src.database.models import Meal
from src.schemas.meals import CreateMealModel, UpdateMealModel


async def add_meal(body: CreateMealModel, db: Session):
    meal = Meal(**body.model_dump())
    if await find_meal_by_name(meal.name, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DUPLICATE_MEAL_NAME.format(meal_name=meal.name))
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal


async def update_meal(body: UpdateMealModel, db: Session):
    meal = Meal(**body.model_dump())
    existing_meal_name = await find_meal_by_name(meal.name, db)
    if existing_meal_name and (meal.id != existing_meal_name.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DUPLICATE_MEAL_NAME.format(meal_name=meal.name))
    db.merge(meal)
    db.commit()
    db.refresh(meal)
    return meal


async def get_meal_all(db: Session):
    return db.query(Meal).all()


async def get_meal(id: UUID, db: Session):
    return db.query(Meal).filter(Meal.id == id).first()


async def find_meal_by_name(name: str, db: Session):
    return db.query(Meal).filter(Meal.name == name).first()


async def delete_meal(id: UUID, db: Session):
    count = db.query(Meal).filter(Meal.id == id).delete()
    db.commit()
    return count


async def set_file_name(id: UUID, file_name: str, db: Session):
    meal = db.query(Meal).filter(Meal.id == id).first()
    if meal:
        meal.image = file_name
        db.commit()
        db.refresh(meal)
    return meal
