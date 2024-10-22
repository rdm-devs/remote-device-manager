import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, BackgroundTasks, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.database import get_db
from src.user.schemas import User, UserCreate
from src.user.service import check_username_exists, create_user
from typing import Any, Dict, Optional
from src.auth.utils import (
    authenticate_user,
    create_access_token,
    get_refresh_token_settings,
    create_connection_token,
    is_valid_otp,
)
from src.auth.dependencies import (
    get_current_active_user,
    valid_refresh_token,
    valid_refresh_token_user,
    has_access_to_device,
)
from src.auth.schemas import LoginData, Token, ConnectionToken
from src.auth import service
from src.device.utils import get_device_by_serialno

load_dotenv()
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
async def login(
    response: Response,
    serialno: Optional[str] = None,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> LoginData:
    user = authenticate_user(form_data.username, form_data.password, db)
    refresh_token_value = await service.create_refresh_token(db, user.id)
    response.set_cookie(**get_refresh_token_settings(refresh_token_value))
    device = get_device_by_serialno(db, serialno)
    return LoginData(
        access_token=create_access_token(user),
        refresh_token=refresh_token_value,
        device=device,
    )


@router.put("/token", response_model=Token)
async def refresh_tokens(
    worker: BackgroundTasks,
    response: Response,
    db: Session = Depends(get_db),
    user=Depends(valid_refresh_token_user),
    refresh_token=Depends(valid_refresh_token),
):
    new_access_token = create_access_token(user)
    new_refresh_token = await service.create_refresh_token(
        db, refresh_token.user_id, refresh_token=refresh_token
    )
    response.set_cookie(**get_refresh_token_settings(new_refresh_token))

    # worker.add_task(service.expire_refresh_token, refresh_token_id=refresh_token.id, db=db)
    return Token(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post("/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db=db, user=user)
    return db_user


@router.delete("/token")
async def logout_user(
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: Dict[str, Any] = Depends(valid_refresh_token),
) -> dict:
    await service.expire_refresh_token(db, refresh_token.refresh_token)

    response.delete_cookie(
        **get_refresh_token_settings(refresh_token.refresh_token, expired=True)
    )

    return {
        "msg": "Logged out succesfully!",
    }


@router.get("/device/{device_id}/connect/{otp}", response_model=dict)
async def get_device_connection_token(
    device_id: int,
    db: Session = Depends(get_db),
    otp: str = Depends(is_valid_otp),
    # user: User = Depends(get_current_active_user),
) -> dict:
    conn_token = create_connection_token(db, device_id)
    return {"token": conn_token}
