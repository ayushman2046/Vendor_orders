import asyncio
import json
import os
import sys
import redis.asyncio as redis
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from app.schemas.events import OrderEvent as OrderEventSchema
from app.db.session import SessionLocal
from app.models.order_events import OrderEvent as OrderEventModel
from app.core.redis_client import redis_client

STREAM_NAME = "vendor_orders"
GROUP_NAME = "order_processor_group"
CONSUMER_NAME = "consumer_1"

async def process_event(event_id: str, event_data: dict):
    db = SessionLocal()

    try:
        raw_event = event_data.get("event")
        if not raw_event:
            print(" No 'event' field in message.")
            return

        event_dict = json.loads(raw_event)
        data = OrderEventSchema(**event_dict)

        total_amount = sum(item.qty * item.unit_price for item in data.items)
        high_value = total_amount > 1000.0

        order_event = OrderEventModel(
            order_id=data.order_id,
            vendor_id=data.vendor_id,
            event_type="order_created",
            payload=event_dict,
            timestamp=data.timestamp,
            total_amount=total_amount,
            high_value=high_value,
        )

        db.add(order_event)
        db.flush()  # Force SQLAlchemy to send INSERT to DB to catch issues early
        db.commit()
        print("Saved to database.")

        # Extra Debug: Check DB rows immediately
        result = db.query(OrderEventModel).count()
        print(f"📊 Total records in DB: {result}")

    except SQLAlchemyError as e:
        db.rollback()
        print(f"DB error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        db.close()

async def consume():
    try:
        print("Connecting to PostgreSQL via SQLAlchemy...")
        try:
            test_db = SessionLocal()
            test_db.execute(text("SELECT 1"))
            print("PostgreSQL connection test passed.")
            test_db.close()
        except Exception as e:
            print(f"Failed PostgreSQL test: {e}")
            sys.exit(1)

        try:
            await redis_client.xgroup_create(STREAM_NAME, GROUP_NAME, id="$", mkstream=True)
            print(f"Consumer group '{GROUP_NAME}' created.")
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                print(f"Consumer group '{GROUP_NAME}' already exists.")
            else:
                print(f"Failed to create group: {e}")
                sys.exit(1)

        print("📡 Listening to Redis stream...")

        while True:
            try:
                response = await redis_client.xreadgroup(
                    groupname=GROUP_NAME,
                    consumername=CONSUMER_NAME,
                    streams={STREAM_NAME: ">"},
                    count=10,
                    block=2000
                )

                if response:
                    for stream, messages in response:
                        for message_id, message in messages:
                            await process_event(message_id, message)
                            await redis_client.xack(STREAM_NAME, GROUP_NAME, message_id)
                else:
                    await asyncio.sleep(1)

            except Exception as e:
                print(f"Error processing stream: {e}")
                await asyncio.sleep(3)

    except Exception as e:
        print(f"FATAL: Could not connect or consume: {e}")
        sys.exit(1)

    finally:
        await redis_client.close()

if __name__ == "__main__":
    try:
        asyncio.run(consume()) #----------- to save data in db after stored in redis.
    except KeyboardInterrupt:
        print("shutting down consumer.")
