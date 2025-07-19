from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta

from app.dependencies.db_session import get_db
from app.dependencies.token_auth import verify_token
from app.models.order_events import OrderEvent

metrics_router = APIRouter()

@metrics_router.get("/metrics")
def get_vendor_metrics(vendor_id: str, db: Session = Depends(get_db), auth=Depends(verify_token)):
    try:
        #Total Orders
        total_orders = db.query(func.count()).filter(OrderEvent.vendor_id == vendor_id).scalar()

        #Total Revenue
        total_revenue = db.query(func.sum(OrderEvent.total_amount)).filter(OrderEvent.vendor_id == vendor_id).scalar() or 0

        #High Value Orders
        high_value_orders = db.query(func.count()).filter(
            OrderEvent.vendor_id == vendor_id,
            OrderEvent.high_value == True
        ).scalar()

        #Last 7 Days Volume
        today = datetime.utcnow().date()
        seven_days_ago = today - timedelta(days=7)

        volume_query = (
            db.query(
                cast(OrderEvent.timestamp, Date).label("day"),
                func.count().label("count")
            )
            .filter(
                OrderEvent.vendor_id == vendor_id,
                cast(OrderEvent.timestamp, Date) >= seven_days_ago
            )
            .group_by(cast(OrderEvent.timestamp, Date))
            .all()
        )

        last_7_days_volume = {str(day): count for day, count in volume_query}

        return {
            "vendor_id": vendor_id,
            "total_orders": total_orders or 0,
            "total_revenue": total_revenue or 0,
            "high_value_orders": high_value_orders or 0,
            "anomalous_orders": 0,
            "last_7_days_volume": last_7_days_volume
        }

    except Exception as e:
        print(f"Error while fetching metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
