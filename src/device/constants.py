class ErrorCode:
    DEVICE_NOT_FOUND = "Device not found."
    DEVICE_NAME_TAKEN = "Device name already taken."
    DEVICE_CREDENTIALS_NOT_CONFIGURED = (
        "Device's remote management credentials are invalid."
    )
    EXPIRED_SHARE_URL = "The URL provided has expired!"
    INVALID_EXPIRATION_MINUTES = "Expiration minutes should be either a positive value or zero."