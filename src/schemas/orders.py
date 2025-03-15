from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, constr


class OrderMealItems(BaseModel):
    id: UUID
    quantity: int = Field(..., gt=0)


class OrderMealOut(BaseModel):
    id: UUID
    name: str
    price: float
    description: str | None
    image: str | None
    quantity: int

    model_config = {
        "from_attributes": True
    }


class OrderCreateCustomer(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    email: EmailStr
    street: constr(strip_whitespace=True, min_length=1)
    city: constr(strip_whitespace=True, min_length=1)
    postal_code: constr(strip_whitespace=True, min_length=1) = Field(..., alias="postal-code")


class OrderOutCustomer(BaseModel):
    name: str
    email: str
    street: str
    city: str
    postal_code: str = Field(..., alias="postal-code")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


class OrderCreate(BaseModel):
    customer: OrderCreateCustomer
    items: List[OrderMealItems] = Field(..., min_items=1)


class OrderOut(BaseModel):
    id: UUID
    customer: OrderOutCustomer
    items: List[OrderMealOut]
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }
