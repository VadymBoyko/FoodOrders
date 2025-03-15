from uuid import UUID

from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.config.messages import CREATE_ORDER_ERROR, MEALS_NOT_FOUND
from src.database.models import Meal, Order, order_meals
from src.schemas.orders import OrderCreate, OrderOut, OrderOutCustomer, OrderMealOut


async def get_order_by_id(id: UUID, db: Session):
    db_order = db.query(Order).filter(Order.id == id).first()
    if not db_order:
        return None

    order_items = (
        db.query(Meal, order_meals.c.quantity)
        .join(order_meals, Meal.id == order_meals.c.meal_id)
        .filter(order_meals.c.order_id == id)
        .all()
    )

    return OrderOut(
        id=db_order.id,
        customer=OrderOutCustomer(
            name=db_order.customer_name,
            email=db_order.customer_email,
            street=db_order.customer_street,
            city=db_order.customer_city,
            postal_code=db_order.customer_postal_code,
        ),
        items=[
            OrderMealOut(
                id=meal.id,
                name=meal.name,
                price=meal.price,
                description=meal.description,
                image=meal.image,
                quantity=quantity,
            )
            for meal, quantity in order_items
        ],
        created_at=db_order.created_at,
        updated_at=db_order.updated_at,
    )



async def get_orders_by_customer_info_mask(search_term: str, db: Session):
    orders = (
        db.query(Order)
        .filter(
            or_(
                Order.customer_email.like(f'%{search_term}%'),
                Order.customer_name.like(f'%{search_term}%'),
                Order.customer_street.like(f'%{search_term}%'),
                Order.customer_city.like(f'%{search_term}%'),
                Order.customer_postal_code.like(f'%{search_term}%')
            )
        )
        .order_by(Order.created_at.desc())
        .all()
    )

    if not orders:
        return []

    order_ids = [order.id for order in orders]
    order_items = (
        db.query(Meal, order_meals.c.order_id, order_meals.c.quantity)
        .join(order_meals, Meal.id == order_meals.c.meal_id)
        .filter(order_meals.c.order_id.in_(order_ids))
        .all()
    )

    items_by_order = {}
    for meal, order_id, quantity in order_items:
        if order_id not in items_by_order:
            items_by_order[order_id] = []
        items_by_order[order_id].append(
            OrderMealOut(
                id=meal.id,
                name=meal.name,
                price=meal.price,
                description=meal.description,
                image=meal.image,
                quantity=quantity,
            )
        )

    return [
        OrderOut(
            id=order.id,
            customer=OrderOutCustomer(
                name=order.customer_name,
                email=order.customer_email,
                street=order.customer_street,
                city=order.customer_city,
                postal_code=order.customer_postal_code,
            ),
            items=items_by_order.get(order.id, []),
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
        for order in orders
    ]


async def get_orders_by_meal_id(meal_id: int, db: Session):
    orders = (
        db.query(Order)
        .join(order_meals, Order.id == order_meals.c.order_id)  # Соединяем с таблицей связи заказов и блюд
        .filter(order_meals.c.meal_id == meal_id)  # Фильтруем по meal_id
        .order_by(Order.created_at.desc())  # Сортируем по дате создания (новые сначала)
        .all()
    )

    if not orders:
        return []

    order_ids = [order.id for order in orders]
    order_items = (
        db.query(Meal, order_meals.c.order_id, order_meals.c.quantity)
        .join(order_meals, Meal.id == order_meals.c.meal_id)
        .filter(order_meals.c.order_id.in_(order_ids))
        .all()
    )

    items_by_order = {}
    for meal, order_id, quantity in order_items:
        if order_id not in items_by_order:
            items_by_order[order_id] = []
        items_by_order[order_id].append(
            OrderMealOut(
                id=meal.id,
                name=meal.name,
                price=meal.price,
                description=meal.description,
                image=meal.image,
                quantity=quantity,
            )
        )

    return [
        OrderOut(
            id=order.id,
            customer=OrderOutCustomer(
                name=order.customer_name,
                email=order.customer_email,
                street=order.customer_street,
                city=order.customer_city,
                postal_code=order.customer_postal_code,
            ),
            items=items_by_order.get(order.id, []),
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
        for order in orders
    ]


async def create_order(order: OrderCreate, db: Session):
    try:
        meal_ids = [meal.id for meal in order.items]
        existing_meals = db.query(Meal.id).filter(Meal.id.in_(meal_ids)).all()
        existing_meal_ids = {meal.id for meal in existing_meals}

        missing_meals = set(meal_ids) - existing_meal_ids
        if missing_meals:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=MEALS_NOT_FOUND.format(meals=missing_meals))

        order_in_db = Order(
            customer_name=order.customer.name,
            customer_email=order.customer.email,
            customer_street=order.customer.street,
            customer_city=order.customer.city,
            customer_postal_code=order.customer.postal_code,
        )
        db.add(order_in_db)
        db.flush()

        order_meal_entries = []
        for item in order.items:
            order_meal_entries.append({
                "order_id": order_in_db.id,
                "meal_id": item.id,
                "quantity": item.quantity
            })

        db.execute(order_meals.insert(), order_meal_entries)
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=CREATE_ORDER_ERROR.format(error=str(e)))

    db.refresh(order_in_db)

    return await get_order_by_id(order_in_db.id, db)
