from src.user_group.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class UserGroupNotFoundError(NotFound):
    DETAIL = ErrorCode.USER_GROUP_NOT_FOUND


class UserGroupNameTakenError(BadRequest):
    DETAIL = ErrorCode.USER_GROUP_NAME_TAKEN

class UserGroupInvalidNameError(BadRequest):
    DETAIL = ErrorCode.USER_GROUP_INVALID_NAME