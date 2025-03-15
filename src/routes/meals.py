from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status, File, UploadFile, APIRouter
from sqlalchemy.orm import Session

from src.config.messages import ERROR_UPLOAD_FILE, MEAL_NOT_FOUND, ERROR_DELETE_MEAL, PROHIBITED_FILE_CONTENT
from src.database.db import get_db
from src.schemas.meals import CreateMealModel, Meal, UpdateMealModel
from src.repository import meals as repository_meals
from src.services.files import update_file, delete_file

router = APIRouter(prefix="/meals", tags=['meals'])


@router.post('/', name='Create new meal',
             status_code=status.HTTP_201_CREATED)
async def create_meal(body: CreateMealModel, db: Session = Depends(get_db)):
    meal = await repository_meals.add_meal(body, db)
    return meal


@router.put('/', name='Update meal',
             status_code=status.HTTP_201_CREATED)
async def update_meal(body: UpdateMealModel, db: Session = Depends(get_db)):
    meal = await repository_meals.get_meal(body.id, db)
    if meal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await repository_meals.update_meal(body, db)



@router.get("/", name="Return all meals",
            response_model=List[Meal],
            status_code=status.HTTP_200_OK)
async def get_all_meals(db: Session = Depends(get_db)):
    return await repository_meals.get_meal_all(db) or []


@router.get("/{id}", name="Return meal",
            response_model=Meal,
            status_code=status.HTTP_200_OK)
async def get_meal_by_id(id: UUID, db: Session = Depends(get_db)):
    meal = await repository_meals.get_meal(id, db)
    if meal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=MEAL_NOT_FOUND.format(id=id))
    return meal


@router.delete("/{id}", name="Delete meal",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal_by_id(id: UUID, db: Session = Depends(get_db)):
    meal = await repository_meals.get_meal(id, db)
    if meal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=MEAL_NOT_FOUND.format(id=id))
    try:
        await repository_meals.delete_meal(id, db)
        await delete_file(meal.image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=ERROR_DELETE_MEAL.format(id=id, error=str(e)))
    return None


@router.post("/upload/{id}", name="upload pics",
             response_model=Meal,
             status_code=status.HTTP_200_OK)
async def upload_pics_meal(id: UUID,
                           file: UploadFile = File(...),
                           db: Session = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=PROHIBITED_FILE_CONTENT.format(content_type=file.content_type)
        )
    meal = await repository_meals.get_meal(id, db)
    if meal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=MEAL_NOT_FOUND.format(id=id))
    try:
        file_name = await update_file(file, meal)
        meal = await repository_meals.set_file_name(meal.id, file_name, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=ERROR_UPLOAD_FILE.format(error=str(e)))
    return meal
