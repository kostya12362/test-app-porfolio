from core.schemas import HTTPException
from fastapi import status


class NotAuthenticated(HTTPException):
    def __init__(self):
        super().__init__(
            code="INVALID_AUTHENTICATION",
            status_code=status.HTTP_403_FORBIDDEN,
            message="Not authenticated",
        )


class InvalidCredentials(HTTPException):
    def __init__(self):
        super().__init__(
            code="INVALID_CREDENTIALS",
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid authentication credentials",
        )


class CouldNotValidCredentials(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Could not validate credentials",
            code="INVALID_CREDENTIALS",
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenRevoked(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Token has been revoked",
            code="TOKEN_REVOKED",
            headers={"WWW-Authenticate": "Bearer"},
        )


class IncorrectCredentials(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Incorrect credentials",
            code="INVALID_CREDENTIALS",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidToken(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid token",
            code="INVALID_TOKEN",
            headers={"WWW-Authenticate": "Bearer"},
        )


class BlockedEndpoint(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message="Already authenticated",
            code="INVALID_AUTHENTICATION",
        )
