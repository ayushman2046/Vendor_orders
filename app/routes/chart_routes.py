from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy import Date, func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64

from app.dependencies.db_session import get_db
from app.dependencies.token_auth import verify_token
from app.models.order_events import OrderEvent

chart_router = APIRouter()

@chart_router.get("/metrics/chart")
def chart_metrics(vendor_id: str = Query(...), db: Session = Depends(get_db), auth=Depends(verify_token)):
    try:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=6)  # 7 days total

        # Query for last 7 days
        result = (
            db.query(
                OrderEvent.timestamp.cast(Date).label("date"),
                func.count().label("order_count")
            )
            .filter(OrderEvent.vendor_id == vendor_id)
            .filter(OrderEvent.timestamp >= start_date)
            .group_by("date")
            .order_by("date")
            .all()
        )

        dates = []
        counts = []
        current = start_date

        # Fill gaps for missing dates
        count_map = {row.date: row.order_count for row in result}
        for i in range(7):
            d = current + timedelta(days=i)
            dates.append(str(d))
            counts.append(count_map.get(d, 0))

        # Plot
        plt.figure(figsize=(8, 4))
        plt.plot(dates, counts, marker='o', linestyle='-', color='blue')
        plt.title(f"Order Volume for Vendor {vendor_id}")
        plt.xlabel("Date")
        plt.ylabel("Orders")
        plt.xticks(rotation=45)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)

        img_base64 = base64.b64encode(buf.read()).decode("utf-8")

        return {
            "vendor_id": vendor_id,
            "chart": img_base64
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
