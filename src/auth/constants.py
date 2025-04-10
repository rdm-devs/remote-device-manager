from string import Template


class ErrorCode:
    INCORRECT_USER_OR_PASSWORD = "El nombre de usuario o la contraseña son incorrectos"
    INACTIVE_USER = "Usuario inactivo"
    AUTHENTICATION_REQUIRED = "Autenticación requerida"
    AUTHORIZATION_FAILED = "La autorización ha fallado. El usuario no tiene acceso"
    INVALID_TOKEN = "Token inválido"
    INVALID_CREDENTIALS = "Credenciales inválidas"
    REFRESH_TOKEN_NOT_VALID = "El refresh token es inválido"
    REFRESH_TOKEN_REQUIRED = "El refresh token es requerido en el body o en las cookies"
    INVALID_OTP = "OTP inválido"
    INVALID_PASSWORD_TOKEN = "El token para actualizcación de password es inválido"
    EMAIL_AUTHENTICATION_REQUIRED = "Ha ocurrido un problema con la autenticación de la cuenta de email del servidor."


class Message:
    EMAIL_SENT_MSG = Template("Email a $email enviado con éxito!")
    PASSWORD_UPDATED_MSG = "Contraseña actualizada con éxito!"
    PASSWORD_RECOVERY_EMAIL_BODY = Template(
        f"""\
    Subject: DexKvm password recovery

    Hola, haz click aquí para recuperar tu contraseña: $recovery_url"""
    )
