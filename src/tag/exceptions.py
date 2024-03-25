from src.tag.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class TagNotFound(NotFound):
    DETAIL = ErrorCode.TAG_NOT_FOUND

class TagNameTaken(BadRequest):
    DETAIL = ErrorCode.TAG_NAME_TAKEN