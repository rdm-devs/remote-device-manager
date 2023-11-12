from src.device_group.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class DeviceGroupNotFoundError(NotFound):
    DETAIL = ErrorCode.DEVICE_GROUP_NOT_FOUND


class DeviceGroupNameTakenError(BadRequest):
    DETAIL = ErrorCode.DEVICE_GROUP_NAME_TAKEN


class InvalidDeviceGroupAttrsError(BadRequest):
    DETAIL = ErrorCode.DEVICE_GROUP_INVALID_ATTRS
