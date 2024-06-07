from src.user.constants import ErrorCode
from src.exceptions import NotFound, BadRequest, PermissionDenied


class UserNotFound(NotFound):
    DETAIL = ErrorCode.USER_NOT_FOUND


class UsernameTaken(BadRequest):
    DETAIL = ErrorCode.USERNAME_TAKEN


class UserInvalidPassword(BadRequest):
    DETAIL = ErrorCode.USER_INVALID_PASSWORD


class UserTenantNotAssigned(NotFound):
    DETAIL = ErrorCode.USER_TENANT_NOT_ASSIGNED

class UserCannotDeleteItself(PermissionDenied):
    DETAIL = ErrorCode.USER_CANNOT_DELETE_ITSELF