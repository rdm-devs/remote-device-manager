from src.tenant.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class TenantNotFoundError(NotFound):
    DETAIL = ErrorCode.TENANT_NOT_FOUND


class TenantNameTakenError(BadRequest):
    DETAIL = ErrorCode.TENANT_NAME_TAKEN
