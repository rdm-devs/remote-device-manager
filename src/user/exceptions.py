from src.user.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class UserNotFoundError(NotFound):
    DETAIL = ErrorCode.USER_NOT_FOUND


class UserEmailTakenError(BadRequest):
    DETAIL = ErrorCode.USER_EMAIL_TAKEN


class UserInvalidPasswordError(BadRequest):
    DETAIL = ErrorCode.USER_INVALID_PASSWORD
