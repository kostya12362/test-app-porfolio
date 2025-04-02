import typing
from typing import TypeVar
from uuid import uuid4 as uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from core.db.models import DBModel

T = TypeVar("T", bound="User")


class CustomUserModelManager(BaseUserManager, typing.Generic[T]):
    """Custom user model manager"""

    @transaction.atomic
    def create_user(
            self,
            username: str | None,
            password: str | None,
            **extra_fields: typing.Any,
    ) -> T:
        """Creates and saves a new user"""
        if not username:
            raise ValueError("The username cannot be empty")
        user: T = self.model(username=username, password=password, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    @transaction.atomic
    def create_superuser(
            self,
            username: str | None,
            password: str | None,
            **extra_fields: typing.Any,
    ) -> T:
        """Creates and saves a new superuser"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email"""

    id = models.UUIDField(primary_key=True, editable=False, default=uuid)
    email = models.EmailField(
        _("Email"),
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        default=None,
    )
    username = models.CharField(_("Username"), max_length=255, unique=True)
    password = models.CharField(_("Password"), max_length=128)
    is_active = models.BooleanField(_("Is active"), default=True)
    is_staff = models.BooleanField(_("Is staff"), default=False)
    is_superuser = models.BooleanField(_("Is superuser"), default=False)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    USERNAME_FIELD = "username"

    objects = CustomUserModelManager()

    class Meta:
        db_table = "users_user"
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self) -> str:
        return f"{self.username}: {self.id}"


class TokenBlackList(DBModel):
    user: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tokens",
        verbose_name=_("User"),
    )
    token: str = models.TextField(_("Token"), max_length=255, unique=True, editable=False)
    created_at: models.DateTimeField = models.DateTimeField(_("Created at"), auto_now_add=True)


class TelegramAccount(DBModel):
    id: str = models.BigAutoField(_("Tg ID"), primary_key=True)
    username: str = models.CharField(_("Username"), max_length=255, unique=True)
    created_at: models.DateTimeField = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(_("Updated at"), auto_now=True)
    is_active: bool = models.BooleanField(_("Is active"), default=True)

    class Meta:
        db_table = "users_telegram_account"
        verbose_name = _("Telegram Account")
        verbose_name_plural = _("Telegram Accounts")

    def __str__(self) -> str:
        return f"{self.username}: {self.id}"
