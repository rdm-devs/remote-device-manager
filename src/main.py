import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_pagination import add_pagination
from .database import engine, Base
from .auth.router import router as auth_router 
from .device.router import router as device_router
from .folder.router import router as folder_router
from .role.router import router as role_router
from .tag.router import router as tag_router
from .tenant.router import router as tenant_router
from .user.router import router as user_router


load_dotenv()

ENV = os.getenv("ENV")
ROOT_PATH = os.getenv(f"ROOT_PATH_{ENV}")


app = FastAPI(root_path=ROOT_PATH)
origins = [
    # "http://localhost",
    "http://localhost:4200",
    # "http://kvmvm.eastus.cloudapp.azure.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], #["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


add_pagination(app)


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(device_router)
app.include_router(folder_router)
app.include_router(role_router)
app.include_router(tag_router)
app.include_router(tenant_router)
app.include_router(user_router)
