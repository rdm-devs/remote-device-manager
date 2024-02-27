from src.tag.constants import ErrorCode
from src.exceptions import NotFound


class TagNotFoundError(NotFound):
    DETAIL = ErrorCode.TAG_NOT_FOUND
