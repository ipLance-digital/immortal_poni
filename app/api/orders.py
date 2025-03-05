import os
from operator import or_
from uuid import UUID
from app.services.storage import SupabaseStorage
from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload
from app.api.auth import get_current_user
from app.models.orders import Order, OrderAttachment
from app.models.users import Users
from app.schemas.orders import (
    OrderList,
    CreateOrder,
    OrderBase,
    DeleteOrder,
    UpdateOrder,
)
from app.api.users import (
    pg_singleton,
    user_exists,
)
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    File,
)

router = APIRouter()

@router.post("/create", response_model=OrderBase)
async def create_order(
    data: CreateOrder,
    current_user: Users = Depends(get_current_user),
) -> OrderBase:
    """
        Создание нового заказа с возможностью назначения исполнителя.
    """
    async with pg_singleton.session as db:
        if data.assign_to and not await user_exists(db, data.assign_to):
            raise HTTPException(
                status_code=400,
                detail="Assigned user does not exist"
            )
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

@router.get("", response_model=OrderList)
async def get_orders(
    current_user: Users = Depends(get_current_user)
) -> OrderList:
    """
        Получение списка заказов,
        созданных или назначенных текущему пользователю.
    """
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
                .options(
                    selectinload(Order.creator),
                    selectinload(Order.assignee)
                )
            )
            orders = result.scalars().all()
            return OrderList(orders=orders)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )


@router.get("/{order_uuid}", response_model=OrderBase)
async def retrieve_order(
        order_uuid: UUID,
        current_user: Users = Depends(get_current_user),
) -> OrderBase:
    """
        Получение информации о конкретном заказе,
        если он создан или назначен текущему пользователю.
    """
    async with pg_singleton.session as db:
        query = (
            select(Order)
            .where(
                or_(
                    Order.created_by == current_user.id,
                    Order.assign_to == current_user.id
                ),
                Order.id == order_uuid
            )
            .options(
                selectinload(Order.creator),
                selectinload(Order.assignee)
            )
        )
        result = await db.execute(query)
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )
        return order

@router.patch("/update_order/{order_uuid}", response_model=OrderBase)
async def update_order(
    order_uuid: UUID,
    data: UpdateOrder,
    current_user: Users = Depends(get_current_user),
) -> OrderBase:
    """
        Обновление заказа, если он принадлежит текущему пользователю.
    """
    async with pg_singleton.session as db:
        query = select(Order).where(
            Order.id == order_uuid,
            Order.created_by == current_user.id
        )
        result = await db.execute(query)
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )
        update_query = (
            update(Order)
            .where(Order.id == order_uuid)
            .values(**data.dict(exclude_unset=True))
            .returning(Order)
        )
        updated_result = await db.execute(update_query)
        updated_order = updated_result.scalar_one()
        await db.commit()
        return updated_order

@router.delete("/delete_order/{order_uuid}", response_model=DeleteOrder)
async def delete_order(
    order_uuid: UUID,
    current_user: Users = Depends(get_current_user),
) -> DeleteOrder:
    """
        Удаление заказа, если он принадлежит текущему пользователю.
    """
    async with pg_singleton.session as db:
        query = select(Order).where(
            Order.id == order_uuid,
            Order.created_by == current_user.id
        )
        result = await db.execute(query)
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        delete_query = delete(Order).where(Order.id == order_uuid)
        await db.execute(delete_query)
        await db.commit()
        return DeleteOrder(id=order_uuid)

@router.post("/{order_uuid}/attach_file")
async def attach_file_to_order(
    order_uuid: UUID,
    file: SupabaseStorage.upload_file = File(...),
    current_user: Users = Depends(get_current_user),
):
    """
        Прикрепить файл к заказу.
    """
    async with pg_singleton.session as db:
        order = await db.execute(
            select(
                Order
            ).where(
                Order.id == order_uuid,
                Order.created_by == current_user.id
            )
        )
        order = order.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        file_path = f"temp/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        file_id = await SupabaseStorage.upload_file(
            file_path,
            file.filename,
            current_user.id
        )
        attachment = OrderAttachment(order_id=order.id, file_id=file_id)
        db.add(attachment)
        await db.commit()
        os.remove(file_path)
        return {
            "file_id": file_id,
            "message": "File attached successfully"
        }

@router.delete("/{order_uuid}/delete_file/{file_uuid}")
async def delete_file_from_order(
    order_uuid: UUID,
    file_uuid: UUID,
    current_user: Users = Depends(get_current_user),
):
    """
        Удалить файл из заказа.
    """
    async with pg_singleton.session as db:
        order = await db.execute(
            select(Order).where(
                Order.id == order_uuid,
                Order.created_by == current_user.id
            )
        )
        order = order.scalar_one_or_none()
        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )
        file_record = await db.execute(
            select(
                OrderAttachment
            ).where(
                OrderAttachment.order_id == order.id,
                OrderAttachment.file_id == str(file_uuid)
            )
        )
        file_record = file_record.scalar_one_or_none()
        if not file_record:
            raise HTTPException(
                status_code=404,
                detail="File not attached to this order"
            )
        await SupabaseStorage.delete_file(file_uuid, current_user.id)
        delete_query = delete(
            OrderAttachment
        ).where(
            OrderAttachment.id == file_record.id
        )
        await db.execute(delete_query)
        await db.commit()
        return {"message": "File deleted successfully"}
