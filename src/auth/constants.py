from string import Template


class ErrorCode:
    INCORRECT_USER_OR_PASSWORD = "Incorrect username or password"
    INACTIVE_USER = "Inactive user"
    AUTHENTICATION_REQUIRED = "Authentication required."
    AUTHORIZATION_FAILED = "Authorization failed. User has no access."
    INVALID_TOKEN = "Invalid token."
    INVALID_CREDENTIALS = "Invalid credentials."
    REFRESH_TOKEN_NOT_VALID = "Refresh token is not valid."
    REFRESH_TOKEN_REQUIRED = "Refresh token is required either in the body or cookie."
    INVALID_OTP = "Invalid OTP."
    INVALID_PASSWORD_TOKEN = "Password update token is not valid."


class Message:
    EMAIL_SENT_MSG = Template("Email to $email sent successfuly!")
