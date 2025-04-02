from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import User, TelegramAccount


class AdminUser(DjangoUserAdmin):
    list_display = (
        "id",
        "email",
        "username",
        "is_active",
        "is_staff",
    )
    readonly_fields = ("last_login", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("email", "password", "username")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Important dates"),
            {"fields": ("created_at", "updated_at", "last_login")},
        ),
    )


class AdminTelegramAccount(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "created_at",
        "is_active",
    )
    readonly_fields = ("created_at",)


# Register your models here.
admin.site.register(User, AdminUser)
admin.site.register(TelegramAccount, AdminTelegramAccount)
admin.autodiscover()
