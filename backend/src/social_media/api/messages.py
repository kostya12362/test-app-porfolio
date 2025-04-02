from core.schemas import HTTPException
from fastapi import status


class AccountNotFound(HTTPException):
    def __init__(self, account_id: int):
        super().__init__(
            message=f"Account with id '{account_id}' not found",
            code="ACCOUNT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )


class AccountAlreadyExists(HTTPException):
    def __init__(self, username: str):
        super().__init__(
            message=f"Account with username `{username}` already exists",
            code="ACCOUNT_ALREADY_EXISTS",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class TagAlreadyExists(HTTPException):
    def __init__(self, title: str):
        super().__init__(
            message=f"Tag with title {title} already exists",
            code="TAG_ALREADY_EXISTS",
            status_code=status.HTTP_400_BAD_REQUEST
       )