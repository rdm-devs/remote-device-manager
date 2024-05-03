from src.tenant.constants import ErrorCode
from src.exceptions import NotFound, BadRequest, PermissionDenied


class TenantNotFound(NotFound):
    DETAIL = ErrorCode.TENANT_NOT_FOUND


class TenantNameTaken(BadRequest):
    DETAIL = ErrorCode.TENANT_NAME_TAKEN


class TenantCannotBeDeleted(PermissionDenied):
    DETAIL = ErrorCode.TENANT_CANNOT_BE_DELETED
