from fastapi import FastAPI
from .user.router import router as user_router
from .user_group.router import router as user_group_router
from .database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_router)
app.include_router(user_group_router)
