from src.entity.constants import ErrorCode
from src.exceptions import NotFound


class EntityNotFound(NotFound):
    DETAIL = ErrorCode.ENTITY_NOT_FOUND