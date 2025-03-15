from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.orders import OrderCreate, OrderOut
from src.repository import orders as repository_orders

router = APIRouter(prefix="/orders", tags=['orders'])


@router.post('/', name='Create new order',
             status_code=status.HTTP_201_CREATED,
             response_model=OrderOut)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    return await repository_orders.create_order(order, db)


@router.get('/{id}', name='Get order by id',
            status_code=status.HTTP_200_OK,
            response_model=OrderOut)
async def get_order_by_id(id: UUID, db: Session = Depends(get_db)):
    order = await repository_orders.get_order_by_id(id, db)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return order


@router.get('/customer/{search_term}', name='Get orders by customer info',
            status_code=status.HTTP_200_OK,
            response_model=List[OrderOut])
async def get_order_by_customer_info_mask(search_term: str, db: Session = Depends(get_db)):
    orders = await repository_orders.get_orders_by_customer_info_mask(search_term, db)
    return orders or []


@router.get('/meal/{meal_id}', name='Get orders by meal',
            status_code=status.HTTP_200_OK,
            response_model=List[OrderOut])
async def get_order_by_customer_info_mask(meal_id: UUID, db: Session = Depends(get_db)):
    orders = await repository_orders.get_orders_by_meal_id(meal_id, db)
    return orders or []
