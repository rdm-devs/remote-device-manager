from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from fastapi.responses import JSONResponse
from src.auth.dependencies import get_current_user
from src.auth.exceptions import InvalidCredentials
from src.database import get_db
from src.audit_mixin import _auth_user_ctx


class AuthUserRequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if (
            "authorization" in request.headers.keys()
            and "Bearer" in request.headers["authorization"]
        ):
            try:
                token = request.headers["authorization"].replace("Bearer ", "")
                user = await get_current_user(token, next(get_db()))
                _auth_user_ctx.set(user.id)
            except InvalidCredentials as exc:
                return JSONResponse(content=exc.detail, status_code=exc.status_code)

        response = await call_next(request)
        return response
