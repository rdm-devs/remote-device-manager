import os
from dotenv import load_dotenv
from fastapi import FastAPI
from .user.router import router as user_router
from .user_group.router import router as user_group_router
from .database import engine, Base

load_dotenv()

ENV = os.getenv("ENV")
ROOT_PATH=os.getenv(f"ROOT_PATH_{ENV}")

Base.metadata.create_all(bind=engine)

app = FastAPI(root_path=ROOT_PATH)

app.include_router(user_router)
app.include_router(user_group_router)
