from operator import or_
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.api.auth import get_current_user
from app.api.users import pg_singleton, user_exists
from app.models.orders import Order
from app.models.users import Users
from app.schemas.order import OrderList, CreateOrder, OrderBase

router = APIRouter()

@router.get("", response_model=OrderList)
async def get_orders(
    current_user: Users = Depends(get_current_user)
):
    try:
        async with pg_singleton.session as db:
            result = await db.execute(
                select(Order)
                .where(
                    or_(
                        Order.created_by == current_user.id,
                        Order.assign_to == current_user.id
                    )
                )
                .options(selectinload(Order.creator), selectinload(Order.assignee))
            )
            orders = result.scalars().all()
            return {"orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/create", response_model=OrderBase)
async def create_order(
    data: CreateOrder,
    current_user: Users = Depends(get_current_user),
):
    async with pg_singleton.session as db:
        if data.assign_to and not await user_exists(db, data.assign_to):
            raise HTTPException(status_code=400,
                                detail="Assigned user does not exist")

        order = Order(
            name=data.name,
            body=data.body,
            price=data.price,
            created_by=current_user.id,
            assign_to=data.assign_to,
            status_id=data.status,
            deadline=data.deadline,
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        return order