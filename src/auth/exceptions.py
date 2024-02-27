from src.auth.constants import ErrorCode
from src.exceptions import BadRequest, NotAuthenticated


class IncorrectUserOrPasswordError(BadRequest):
    DETAIL = ErrorCode.INCORRECT_USER_OR_PASSWORD


class InactiveUserError(BadRequest):
    DETAIL = ErrorCode.INACTIVE_USER


class InvalidCredentialsError(NotAuthenticated):
    DETAIL = ErrorCode.AUTHENTICATION_REQUIRED


class RefreshTokenNotValid(NotAuthenticated):
    DETAIL = ErrorCode.REFRESH_TOKEN_NOT_VALID
