from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from django.conf import settings
from django.contrib.auth import aauthenticate
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from jwt.exceptions import InvalidTokenError

from core.db.utils import AsyncAtomicContextManager
from users.api.exceptions import (
    NotAuthenticated,
    InvalidCredentials,
    CouldNotValidCredentials,
    TokenRevoked,
    IncorrectCredentials,
    InvalidToken,
    BlockedEndpoint
)
from users.api.schemas import TokenSchemaResponse
from users.models import User, TokenBlackList

__all__ = ("user_auth",)


class OAuth2PasswordBearerJSON(HTTPBearer):
    header_name = "Authorization"
    schema = settings.AUTHENTICATION.scheme

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        authorization = request.headers.get(self.header_name)
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise NotAuthenticated
            else:
                return None
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise InvalidCredentials
            else:
                return None
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


oauth2_scheme = OAuth2PasswordBearerJSON()


class UserAuth:
    SECRET_KEY = settings.AUTHENTICATION.access_token.secret_key
    ALGORITHM = settings.AUTHENTICATION.algorithm

    @classmethod
    def create_access_token(cls, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()  # copy data for encoding
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})  # current live time
        encoded_jwt = jwt.encode(
            payload=to_encode, key=cls.SECRET_KEY, algorithm=cls.ALGORITHM
        )
        return encoded_jwt

    @classmethod
    def decode_token(cls, token: str) -> dict:
        return jwt.decode(jwt=token, key=cls.SECRET_KEY, algorithms=cls.ALGORITHM)

    @classmethod
    async def validate_user(cls, username: str, password: str) -> User | None:
        user: User | None = await aauthenticate(username=username, password=password)
        if user is None:
            raise InvalidCredentials
        if user.is_active is True:
            return user
        return None

    @classmethod
    async def get_current_user(
            cls, model: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]
    ) -> User:
        # Exception for invalid credentials
        try:
            # Decode token
            payload = cls.decode_token(model.credentials)
            # Data from token
            user_id: str = str(payload.get("id"))
            username: str = str(payload.get("username"))
            exp: str = str(payload.get("exp"))
            if username is None:
                raise CouldNotValidCredentials
            # If token is expired
            if datetime.fromtimestamp(float(exp), tz=timezone.utc) < datetime.now(
                    timezone.utc
            ):
                raise CouldNotValidCredentials
            # Check if token is blacklisted
            is_blacklisted = await TokenBlackList.objects.filter(token=model.credentials).aexists()
            if is_blacklisted:
                raise TokenRevoked
        except InvalidTokenError:
            raise CouldNotValidCredentials

        # Check user
        user: User | None = await User.objects.filter(
            id=user_id, username=username, is_active=True
        ).afirst()

        if user is None:
            raise CouldNotValidCredentials
        return user

    async def login_for_access_token(
            self, username: str, password: str
    ) -> TokenSchemaResponse:
        user: User | None = await self.validate_user(
            username, password
        )  # Validate user
        if not user:
            raise IncorrectCredentials

        access_token_expires = timedelta(seconds=settings.AUTHENTICATION.access_token.ttl)  # Delta lifetime
        # Data for decoding
        access_token = self.create_access_token(
            data={
                "id": str(user.id),  # UUID
                "email": user.email,
                "username": user.username,
            },
            expires_delta=access_token_expires,
        )  # Create access token

        return TokenSchemaResponse(
            access_token=access_token,
            token_type=oauth2_scheme.schema,
            access_token_expires=access_token_expires.total_seconds(),
        )

    @classmethod
    async def logout(cls, model: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]):
        """Logs out the user and revokes the token by adding it to the blacklist"""
        try:
            user: User = await cls.get_current_user(model)
            # Store the token in the blacklist with its expiration timestamp
            async with AsyncAtomicContextManager():
                await TokenBlackList.objects.acreate(
                    token=model.credentials,
                    user=user,
                )
                user.last_login = datetime.now()
                await user.asave(update_fields=["last_login"])

        except InvalidTokenError:
            raise InvalidToken

    @staticmethod
    def block_endpoint(request: Request):
        if request.headers.get(oauth2_scheme.header_name):
            raise BlockedEndpoint


user_auth = UserAuth()
