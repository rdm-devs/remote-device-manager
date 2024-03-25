from src.tenant.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class TenantNotFound(NotFound):
    DETAIL = ErrorCode.TENANT_NOT_FOUND


class TenantNameTaken(BadRequest):
    DETAIL = ErrorCode.TENANT_NAME_TAKEN
