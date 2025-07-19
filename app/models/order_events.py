from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, Boolean
from datetime import datetime
from app.db.session import Base

class OrderEvent(Base):
    __tablename__ = "order_events"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, nullable=False)
    vendor_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    total_amount = Column(Float, nullable=True)
    high_value = Column(Boolean, default=False)
