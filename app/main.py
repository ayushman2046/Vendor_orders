from fastapi import FastAPI
from app.routes.event_routes import event_router
from app.routes.metrics_routes import metrics_router
from app.db.session import Base, engine
from contextlib import asynccontextmanager
from app.routes.query_routes import query_router
from app.routes.chart_routes import chart_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

# Register routes
app.include_router(event_router)
app.include_router(metrics_router)
app.include_router(query_router)
app.include_router(chart_router)
