from src.auth.constants import ErrorCode
from src.exceptions import BadRequest, NotAuthenticated


class IncorrectUserOrPasswordError(BadRequest):
    DETAIL = ErrorCode.INCORRECT_USER_OR_PASSWORD


class InactiveUserError(BadRequest):
    DETAIL = ErrorCode.INACTIVE_USER


class InvalidCredentialsError(NotAuthenticated):
    pass
