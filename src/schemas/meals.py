from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, constr


class CreateMealModel(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    price: float
    description: Optional[str] = None


class UpdateMealModel(BaseModel):
    id: UUID
    name: constr(strip_whitespace=True, min_length=1)
    price: float
    description: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class Meal(BaseModel):
    id: UUID
    name: str
    price: float
    description: Optional[str] = None
    image: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class MealOrderItem(BaseModel):
    id: UUID
    name: str
    price: float
    description: Optional[str] = None
    image: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
