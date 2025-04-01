import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, BackgroundTasks, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.database import get_db
from src.exceptions import PermissionDenied
from src.user.schemas import User, UserCreate
from src.user.service import check_username_exists, create_user, get_user
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
    has_admin_or_owner_role,
    has_access_to_user
)
from src.auth.schemas import (
    LoginData,
    Token,
    ConnectionToken,
    DeviceLoginData,
    ForgotPasswordData,
    ForgotPasswordEmailSent,
    PasswordUpdateData,
    PasswordUpdated,
    PasswordResetData,
)
from src.auth import service
from src.device.utils import get_device_by_serial_number
from src.device import exceptions as device_exceptions

load_dotenv()
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
async def login(
    response: Response,
    serial_number: Optional[str] = None,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> LoginData:
    user = authenticate_user(form_data.username, form_data.password, db)
    refresh_token_value = await service.create_refresh_token(db, user.id, serial_number)
    response.set_cookie(**get_refresh_token_settings(refresh_token_value))
    device = get_device_by_serial_number(db, serial_number)
    return LoginData(
        access_token=create_access_token(user, serial_number),
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
        db, refresh_token.user_id, serial_number=refresh_token.serial_number
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
    await service.delete_refresh_token(db, refresh_token.refresh_token)

    response.delete_cookie(
        **get_refresh_token_settings(refresh_token.refresh_token, expired=True)
    )

    return {
        "msg": "La sesión se ha cerrado exitosamente!",
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


@router.post("/device/{device_id}/login", response_model=LoginData)
async def device_login(
    response: Response,
    device_id: int,
    device_login_data: DeviceLoginData,
    db: Session = Depends(get_db),
) -> LoginData:
    refresh_token = device_login_data.refresh_token
    user_id, serial_number = await service.get_auth_data_from_token(db, refresh_token)
    user = get_user(db, user_id)
    device = get_device_by_serial_number(db, serial_number)
    if not device:
        raise device_exceptions.DeviceNotFound()

    refresh_token_value = await service.create_refresh_token(db, user_id, serial_number)
    response.set_cookie(**get_refresh_token_settings(refresh_token_value))

    return LoginData(
        access_token=create_access_token(user, serial_number),
        refresh_token=refresh_token_value,
        device=device,
    )


@router.post("/forgot-password")
async def forgot_password(
    forgot_password_data: ForgotPasswordData,
    db: Session = Depends(get_db),
) -> ForgotPasswordEmailSent:
    return service.send_password_recovery_email(db, forgot_password_data)


@router.post("/password-recovery")
async def password_recovery(
    token: str,
    password_update_data: PasswordUpdateData,
    db: Session = Depends(get_db),
) -> PasswordUpdated:
    return service.update_user_password(db, token, password_update_data)


@router.post("/password-reset")
async def password_reset(
    password_reset_data: PasswordResetData,
    user = Depends(has_admin_or_owner_role),
    db: Session = Depends(get_db),
) -> PasswordUpdated:
    if password_reset_data.user_id:
        if not await has_access_to_user(password_reset_data.user_id, db, user):
            raise PermissionDenied()
    return service.reset_user_password(db, user, password_reset_data)
