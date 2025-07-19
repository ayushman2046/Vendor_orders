import uvicorn
from app.db.session import engine
from app.db.session import Base

if __name__ == '__main__':
    print("Creating database tables")
    Base.metadata.create_all(bind=engine)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)