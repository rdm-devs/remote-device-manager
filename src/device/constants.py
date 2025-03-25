class ErrorCode:
    DEVICE_NOT_FOUND = "Dispositivo no encontrado"
    DEVICE_NAME_TAKEN = "Otro dispositivo tiene este nombre"
    DEVICE_CREDENTIALS_NOT_CONFIGURED = (
        "Las credenciales para la gestion remota del dispositivo son inválidas"
    )
    EXPIRED_SHARE_URL = "La URL provista ha expirado!"
    INVALID_EXPIRATION_MINUTES = "Los minutos de expiración deben expresarse como enteros positivos o cero"