import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import F, Q, Count
from django.db.models.functions import JSONObject
from django.contrib.postgres.aggregates import ArrayAgg

from core.db.models import DBModel
from users.models import User


class UserSubscription(DBModel):
    """UserByAccount model"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey("Account", on_delete=models.CASCADE, related_name="subscriptions")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='subscriptions')
    follow_tags = models.ManyToManyField("Tag", related_name="followed_by", blank=True)

    class Meta:
        verbose_name = _("User Subscription")
        verbose_name_plural = _("User Subscription")
        indexes = (models.Index(fields=["account", "user"]),)

    def __str__(self) -> str:
        return f"{self.account.username} - {self.user.username}"


class Account(DBModel):
    """Account model"""

    class Provider(models.TextChoices):
        INSTAGRAM = "INSTAGRAM", _('Instagram')

    id = models.BigAutoField(primary_key=True)
    username = models.CharField(_("Username"), max_length=255)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    provider = models.CharField(
        _("Provider social media"), max_length=255, choices=Provider.choices, default=Provider.INSTAGRAM
    )

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        indexes = (models.Index(fields=["provider", "username"]),)
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.username

    @classmethod
    def extract(cls, user: User, tags_limit: int = None):
        return cls.objects.filter(
            subscriptions__user=user.id
        ).annotate(
            total_tags=Count("subscriptions__follow_tags", distinct=True),
            tags_items=ArrayAgg(
                JSONObject(
                    id=F("subscriptions__follow_tags__id"),
                    title=F("subscriptions__follow_tags__title"),
                ),
                filter=Q(subscriptions__follow_tags__id__isnull=False),
                distinct=True,
                default=[]
            )
        ).annotate(
            tags=JSONObject(
                total=F("total_tags"),
                items=F("tags_items")[:tags_limit]
            )
        )


class Tag(DBModel):
    """Tags model"""

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(_("Name"), max_length=255, unique=True)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self) -> str:
        return self.title


class Post(DBModel):
    """Post model"""

    id = models.BigAutoField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    description = models.TextField(_("Description"))
    likes = models.PositiveIntegerField(_("Likes"), default=0)
    comments = models.PositiveIntegerField(_("Comments"), default=0)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    store_at = models.DateTimeField(_("Updated at"), auto_now=True)
    tags = models.ManyToManyField(Tag, related_name="posts")
    uid = models.CharField(_("Provider ID"), max_length=255, null=True)

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        constraints = [
            models.UniqueConstraint(fields=['account', 'uid'], name='unique_account_provider_uid')
        ]

    def __str__(self) -> str:
        return str(self.id)

    @classmethod
    def extract(cls, user: User):
        fields = cls.get_fields()
        fields.remove('tags')
        fields.remove('account')
        return cls.objects.filter(
            account__subscriptions__user=user.id
        ).select_related('account').values(*fields).annotate(
            username=F("account__username"),
            tags=JSONObject(
                total=Count("tags__id", distinct=True),
                items=ArrayAgg(
                    JSONObject(
                        id=F("tags__id"),
                        title=F("tags__title"),
                    ),
                    filter=Q(tags__id__isnull=False),
                    distinct=True,
                    default=[],
                    offset=0,
                    limit=1
                )
            )
        )
