from src.device_os.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class DeviceOSNotFoundError(NotFound):
    DETAIL = ErrorCode.DEVICE_OS_NOT_FOUND


class DeviceOSNameTakenError(BadRequest):
    DETAIL = ErrorCode.DEVICE_OS_NAME_TAKEN
