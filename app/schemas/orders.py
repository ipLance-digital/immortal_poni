from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional, List

class OrderBase(BaseModel):
    id: UUID
    name: str
    body: str
    price: int
    created_by: UUID
    assign_to: Optional[UUID]
    status_id: int
    created_at: datetime
    deadline: Optional[datetime]
    attachments: Optional[str]

    class Config:
        from_attributes = True


class OrderList(BaseModel):
    orders: List[OrderBase]

    class Config:
        from_attributes = True


class CreateOrder(BaseModel):
    name: str
    body: str
    price: int
    assign_to: Optional[UUID]
    status: int = 1
    deadline: Optional[datetime]

    class Config:
        from_attributes = True


class DeleteOrder(BaseModel):
    id: Optional[UUID]


class UpdateOrder(BaseModel):
    name: Optional[str] = None
    body: Optional[str] = None
    price: Optional[float] = None
    assign_to: Optional[int] = None
    status_id: Optional[int] = None
    deadline: Optional[datetime] = None
