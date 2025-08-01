# Vendor Orders - Event-Driven Backend

A backend system for processing vendor order events asynchronously, computing analytics, and enabling natural language queries. Built with FastAPI, Redis Streams, PostgreSQL, and LangChain.

---

## Features

- **POST /events**  
  Accepts vendor orders, pushes them to Redis Stream for async processing.

- **Redis Consumer**  
  Listens for events, computes:
  - `total_amount` = qty × unit_price  
  - Flags `high_value` if total > 500  
  - Persists to PostgreSQL

- **GET /metrics?vendor_id=...**  
  Returns aggregated metrics for a vendor:
  - total orders  
  - total revenue  
  - high value orders  
  - 7-day order volume

- **POST /query**  
  Accepts a natural language question and uses LangChain to fetch the answer from the database.

- **Token-based Authentication**  
  All APIs require a valid token via `Authorization` header.

---

## Project Structure

```
vendor_orders/
├── app/
│   ├── main.py                      # FastAPI app
│   ├── core/redis_client.py         # Redis connection
│   ├── db/session.py                # SQLAlchemy DB setup
│   ├── dependencies/
│   │   ├── db_session.py            # DB dependency
│   │   └── auth_token.py            # Token auth logic
│   ├── routes/
│   │   ├── event_routes.py          # /events endpoint
│   │   ├── metrics_routes.py        # /metrics endpoint
│   │   └── query_routes.py          # /query endpoint
│   ├── consumers/redis_consumer.py  # Redis event processor
│   ├── models/order_events.py       # Order model
│   ├── schemas/events.py            # Pydantic schemas
│   └── langchain/invoke_langchain.py # LangChain logic
├── run.py                           # Entrypoint
├── Dockerfile                       # App Dockerfile
├── docker-compose.yml               # Stack config
├── .env                             # Environment vars
├── requirements.txt                 # Python packages
```

---

## Setup & Run

```bash
docker-compose up --build
```

Make sure `.env` has correct values:

```env
DATABASE_URL=postgresql://user:password@db:5432/postgres
API_AUTH_TOKEN=your-secret-token
REDIS_URL=redis://redis:6379/0
```

---

## Authentication

All requests must include:

```
Authorization: Bearer your-secret-token
```

---

## Example Usage

### POST /events

```bash
curl -X POST http://localhost:8000/events  \
  -H "Authorization: Bearer your-secret-token"  \
  -H "Content-Type: application/json"  \
  -d '{
   "vendor_id": "V001",
   "order_id": "ORD123",
   "items": [
     { "sku": "SKU1", "qty": 2, "unit_price": 120 },
     { "sku": "SKU2", "qty": 1, "unit_price": 50 }
   ],
   "timestamp": "2025-07-04T14:00:00Z"
 }'
```

Response:

```json
{
  "status": "queued",
  "order_id": "ORD123"
}
```

---

### GET /metrics?vendor_id=V001

```bash
curl http://localhost:8000/metrics?vendor_id=V001  \
  -H "Authorization: Bearer your-secret-token"
```

Response:

```json
{
  "vendor_id": "v4",
  "total_orders": 1,
  "total_revenue": 27.47,
  "high_value_orders": 0,
  "anomalous_orders": 0,
  "last_7_days_volume": {
    "2025-07-19": 1
  }
}
```

---

### POST /query

```bash
curl -X POST http://localhost:8000/query  \
  -H "Authorization: Bearer your-secret-token"  \
  -H "Content-Type: application/json"  \
  -d '{"question": "What is the total revenue for vendor V001?"}'
```

Response:

```json
{
  "query": "SELECT total_amount FROM order_events WHERE vendor_id = 'v1';",
  "result": [
    { "total_amount": 27.47 },
    { "total_amount": 27.47 },
    { "total_amount": 27.47 },
    { "total_amount": 27.47 },
    { "total_amount": 27.47 }
  ]
}
```

---

### GET /metrics/chart?vendor_id=V001

```json
{
  "vendor_id": "V001",
  "chart": "<base64-encoded PNG image string>"
}
```

---

## Add-on

- We can easily move LangChain prompt templates into the database for better customization.

---

## Note on `__init__.py`

Almost all `__init__.py` files are empty, but we can use them to initialize each folder—like registering routes, setting up logging, or importing shared modules.

---

## Tech Stack

- FastAPI – Web API  
- Redis Streams – Message queue  
- PostgreSQL – Event store  
- LangChain – AI query interface  
- Docker – Containerization

---

## Ready to Deploy

```bash
docker-compose up --build
```
