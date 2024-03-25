from src.role.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class RoleNotFound(NotFound):
    DETAIL = ErrorCode.ROLE_NOT_FOUND


class RoleNameTaken(BadRequest):
    DETAIL = ErrorCode.ROLE_NAME_TAKEN
