from src.auth.constants import ErrorCode
from src.exceptions import BadRequest, NotAuthenticated


class IncorrectUserOrPassword(BadRequest):
    DETAIL = ErrorCode.INCORRECT_USER_OR_PASSWORD


class InactiveUser(BadRequest):
    DETAIL = ErrorCode.INACTIVE_USER


class InvalidCredentials(NotAuthenticated):
    DETAIL = ErrorCode.AUTHENTICATION_REQUIRED


class RefreshTokenNotValid(NotAuthenticated):
    DETAIL = ErrorCode.REFRESH_TOKEN_NOT_VALID

class InvalidOTP(BadRequest):
    DETAIL = ErrorCode.INVALID_OTP