import uuid

from sqlalchemy import Column, String, DateTime, Numeric, Integer, ForeignKey, Table, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Meal(Base):
    __tablename__ = "meals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(String)
    image = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


order_meals = Table('order_meals', Base.metadata,
                    Column('order_id', UUID(as_uuid=True), ForeignKey('orders.id'), primary_key=True),
                    Column('meal_id', UUID(as_uuid=True), ForeignKey('meals.id'), primary_key=True),
                    Column('quantity', Integer, default=1)
                    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    meals = relationship("Meal", secondary=order_meals, backref="orders")
    customer_name = Column(String(200), nullable=False)
    customer_email = Column(String(255), nullable=False)
    customer_street = Column(String(200), nullable=False)
    customer_city = Column(String(150), nullable=False)
    customer_postal_code = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
