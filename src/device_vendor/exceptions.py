from src.device_vendor.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class DeviceVendorNotFoundError(NotFound):
    DETAIL = ErrorCode.DEVICE_VENDOR_NOT_FOUND


class DeviceVendorBrandNameTakenError(BadRequest):
    DETAIL = ErrorCode.DEVICE_VENDOR_BRAND_NAME_TAKEN
