import os
import uuid
from io import BytesIO
from operator import or_
from uuid import UUID
from app.core.storage import SupabaseStorage
from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload
from app.api.base import BaseApi
from app.models.users import Users
from app.schemas.orders import (
    OrderList,
    CreateOrder,
    OrderBase,
    UpdateOrder,
)
from fastapi import (
    Depends,
    HTTPException,
    File,
    UploadFile,
)
from app.models.orders import (
    Order,
    OrderAttachment,
)


class OrdersApi(BaseApi):
    def __init__(self):
        super().__init__()
        self.router.add_api_route(
            "/create", self.create_order, methods=["POST"], response_model=OrderBase
        )
        self.router.add_api_route(
            "", self.get_orders, methods=["GET"], response_model=OrderList
        )
        self.router.add_api_route(
            "/{order_uuid}",
            self.retrieve_order,
            methods=["GET"],
            response_model=OrderBase,
        )
        self.router.add_api_route(
            "/update_order/{order_uuid}",
            self.update_order,
            methods=["PATCH"],
            response_model=OrderBase,
        )
        self.router.add_api_route(
            "/delete_order/{order_uuid}",
            self.delete_order,
            methods=["DELETE"],
        )
        self.router.add_api_route(
            "/{order_uuid}/attach_file", self.attach_file_to_order, methods=["POST"]
        )
        self.router.add_api_route(
            "/{order_uuid}/delete_file/{file_uuid}",
            self.delete_file_from_order,
            methods=["DELETE"],
        )

    async def create_order(
        self,
        data: CreateOrder,
        current_user: Users = Depends(BaseApi.get_current_user),
    ) -> OrderBase:
        """
        Создание нового заказа с возможностью назначения исполнителя.
        """
        async with self.db as db:
            if data.assign_to and not await self.user_exists(db, data.assign_to):
                raise HTTPException(
                    status_code=400, detail="Assigned user does not exist"
                )
            order = Order(
                name=data.name,
                body=data.body,
                price=data.price,
                created_by=current_user.id,
                assign_to=data.assign_to,
                status_id=data.status,
                deadline=data.deadline,
                attachments=data.attachments,
            )
            db.add(order)
            await self.update_db(db, order)
        return order

    async def get_orders(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> OrderList:
        """
        Получение списка всех заказов с пагинацией
        """
        try:
            async with self.db as db:
                offset = (page - 1) * page_size
                result = await db.execute(select(Order).limit(page_size).offset(offset))
                orders = result.scalars().all()
            return OrderList(orders=orders)
        except Exception:
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def retrieve_order(
        self,
        order_uuid: UUID,
        current_user: Users = Depends(BaseApi.get_current_user),
    ) -> OrderBase:
        """
        Получение информации о конкретном заказе,
        если он создан или назначен текущему пользователю.
        """
        async with self.db as db:
            query = (
                select(Order)
                .where(
                    or_(
                        Order.created_by == current_user.id,
                        Order.assign_to == current_user.id,
                    ),
                    Order.id == order_uuid,
                )
                .options(selectinload(Order.creator), selectinload(Order.assignee))
            )
            result = await db.execute(query)
            order = result.scalar_one_or_none()
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
        return order

    async def update_order(
        self,
        order_uuid: UUID,
        data: UpdateOrder,
        current_user: Users = Depends(BaseApi.get_current_user),
    ) -> OrderBase:
        """
        Обновление заказа, если он принадлежит текущему пользователю.
        """
        async with self.db as db:
            query = select(Order).where(
                Order.id == order_uuid, Order.created_by == current_user.id
            )
            result = await db.execute(query)
            order = result.scalar_one_or_none()
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            update_query = (
                update(Order)
                .where(Order.id == order_uuid)
                .values(**data.model_dump(exclude_unset=True))
                .returning(Order)
            )
            updated_result = await db.execute(update_query)
            updated_order = updated_result.scalar_one()
            await self.update_db(db)
        return updated_order

    async def delete_order(
        self,
        order_uuid: UUID,
        current_user: Users = Depends(BaseApi.get_current_user),
    ):
        """
        Удаление заказа, если он принадлежит текущему пользователю.
        """
        async with self.db as db:
            query = select(Order).where(
                Order.id == order_uuid, Order.created_by == current_user.id
            )
            result = await db.execute(query)
            order = result.scalar_one_or_none()
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            delete_query = delete(Order).where(Order.id == order_uuid)
            await db.execute(delete_query)
            await db.commit()

        return f"Order id {order_uuid} deleted"

    async def attach_file_to_order(
        self,
        order_uuid: uuid.UUID,
        file: UploadFile = File(...),
        current_user: Users = Depends(BaseApi.get_current_user),
    ):
        async with self.db as db:
            order = await db.execute(
                select(Order).where(
                    Order.id == order_uuid, Order.created_by == current_user.id
                )
            )
            order = order.scalar_one_or_none()
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")

            try:
                file_content = await file.read()
                if len(file_content) > 10 * 1024 * 1024:
                    raise HTTPException(status_code=413, detail="File too large")

                file_size = file.size
                file_id = await SupabaseStorage.upload_file(
                    file_obj=file_content,
                    file_name=file.filename,
                    user_id=current_user.id,
                    file_size=file_size,
                    content_type=file.content_type,
                )
                attachment = OrderAttachment(order_id=order.id, file_id=file_id)
                db.add(attachment)
                await db.commit()

                return {"file_id": file_id, "message": "File attached successfully"}

            except Exception as e:
                await db.rollback()
                raise HTTPException(
                    status_code=500, detail=f"Error attaching file: {str(e)}"
                )

    async def delete_file_from_order(
        self,
        order_uuid: UUID,
        file_uuid: UUID,
        current_user: Users = Depends(BaseApi.get_current_user),
    ):
        """
        Удалить файл из заказа.
        """
        async with self.db as db:
            order = await db.execute(
                select(Order).where(
                    Order.id == order_uuid, Order.created_by == current_user.id
                )
            )
            order = order.scalar_one_or_none()
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            file_record = await db.execute(
                select(OrderAttachment).where(
                    OrderAttachment.order_id == order.id,
                    OrderAttachment.file_id == str(file_uuid),
                )
            )
            file_record = file_record.scalar_one_or_none()
            if not file_record:
                raise HTTPException(
                    status_code=404, detail="File not attached to this order"
                )
            await SupabaseStorage.delete_file(file_uuid, current_user.id)
            delete_query = delete(OrderAttachment).where(
                OrderAttachment.id == file_record.id
            )
            await db.execute(delete_query)
            await db.commit()
        return {"message": "File deleted successfully"}
