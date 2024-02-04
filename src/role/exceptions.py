from src.role.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class RoleNotFoundError(NotFound):
    DETAIL = ErrorCode.ROLE_NOT_FOUND


class RoleNameTakenError(BadRequest):
    DETAIL = ErrorCode.ROLE_NAME_TAKEN
