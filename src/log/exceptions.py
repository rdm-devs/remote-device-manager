from src.log.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class LogEntryNotFoundError(NotFound):
    DETAIL = ErrorCode.LOG_ENTRY_NOT_FOUND
