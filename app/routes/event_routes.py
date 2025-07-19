from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.redis_client import redis_client
from app.dependencies.token_auth import verify_token
from app.schemas.events import OrderEvent
from app.dependencies.db_session import get_db

event_router = APIRouter()

@event_router.post("/events")
async def publish_event(event: OrderEvent, db: Session = Depends(get_db), auth=Depends(verify_token)):
    try:
        # Use Pydantic native JSON-safe serialization
        event_data = event.model_dump_json()

        # Redis stream values must be str/int/bytes
        await redis_client.xadd("vendor_orders", {"event": event_data})

        return {"status": "queued", "order_id": event.order_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
