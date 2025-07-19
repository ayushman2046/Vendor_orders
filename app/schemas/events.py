# app/schemas/event.py
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import uuid

class OrderItem(BaseModel):
    sku: str
    qty: int
    unit_price: float

class OrderEvent(BaseModel):
    vendor_id: str
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    items: List[OrderItem]
    timestamp: datetime
