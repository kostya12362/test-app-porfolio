from django.contrib import admin
from social_media.models import Account, Post, Tag, UserSubscription


# Register your models here.


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "provider", "created_at")
    list_filter = ("provider",)
    search_fields = ("username",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "created_at")
    list_filter = ("account",)
    search_fields = ("text",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "title",)
    search_fields = ("title",)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "user")
    list_filter = ("account",)
    search_fields = ("user",)
