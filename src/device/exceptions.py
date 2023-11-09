from src.device.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class DeviceNotFoundError(NotFound):
    DETAIL = ErrorCode.DEVICE_NOT_FOUND


class DeviceNameTakenError(BadRequest):
    DETAIL = ErrorCode.DEVICE_NAME_TAKEN
