from src.entity.constants import ErrorCode
from src.exceptions import NotFound


class EntityNotFoundError(NotFound):
    DETAIL = ErrorCode.ENTITY_NOT_FOUND