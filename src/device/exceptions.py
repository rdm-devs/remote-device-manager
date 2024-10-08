from src.device.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class DeviceNotFound(NotFound):
    DETAIL = ErrorCode.DEVICE_NOT_FOUND


class DeviceNameTaken(BadRequest):
    DETAIL = ErrorCode.DEVICE_NAME_TAKEN


class DeviceCredentialsNotConfigured(BadRequest):
    DETAIL = ErrorCode.DEVICE_CREDENTIALS_NOT_CONFIGURED


class ExpiredShareDeviceURL(BadRequest):
    DETAIL = ErrorCode.EXPIRED_SHARE_URL


class InvalidExpirationHours(BadRequest):
    DETAIL = ErrorCode.INVALID_EXPIRATION_HOURS
