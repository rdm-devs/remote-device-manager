from src.user.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class UserNotFound(NotFound):
    DETAIL = ErrorCode.USER_NOT_FOUND


class UserEmailTaken(BadRequest):
    DETAIL = ErrorCode.USER_EMAIL_TAKEN


class UsernameTaken(BadRequest):
    DETAIL = ErrorCode.USERNAME_TAKEN


class UserInvalidPassword(BadRequest):
    DETAIL = ErrorCode.USER_INVALID_PASSWORD
