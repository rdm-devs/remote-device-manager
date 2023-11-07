import os
from dotenv import load_dotenv
from fastapi import FastAPI
from .user.router import router as user_router
from .user_group.router import router as user_group_router
from .device.router import router as device_router
from .device_group.router import router as device_group_router
from .tenant.router import router as tenant_router
from .database import engine, Base

load_dotenv()

ENV = os.getenv("ENV")
ROOT_PATH=os.getenv(f"ROOT_PATH_{ENV}")


app = FastAPI(root_path=ROOT_PATH)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(user_router)
app.include_router(user_group_router)
app.include_router(device_router)
app.include_router(device_group_router)
app.include_router(tenant_router)