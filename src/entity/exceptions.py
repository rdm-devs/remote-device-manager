from src.entity.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class EntityNotFound(NotFound):
    DETAIL = ErrorCode.ENTITY_NOT_FOUND


class EntityTenantRelationshipMissing(BadRequest):
    DETAIL = ErrorCode.ENTITY_TENANT_RELATIONSHIP_MISSING
