import os
from dotenv import load_dotenv
from fastapi import FastAPI
from .database import engine, Base
from .device.router import router as device_router
from .device_os.router import router as device_os_router
from .device_vendor.router import router as device_vendor_router
from .folder.router import router as folder_router
from .log.router import router as log_router
from .role.router import router as role_router
from .tag.router import router as tag_router
from .tenant.router import router as tenant_router
from .user.router import router as user_router


load_dotenv()

ENV = os.getenv("ENV")
ROOT_PATH = os.getenv(f"ROOT_PATH_{ENV}")


app = FastAPI(root_path=ROOT_PATH)


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(device_router)
app.include_router(device_os_router)
app.include_router(device_vendor_router)
app.include_router(folder_router)
app.include_router(log_router)
app.include_router(role_router)
app.include_router(tag_router)
app.include_router(tenant_router)
app.include_router(user_router)
