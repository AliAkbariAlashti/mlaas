from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("-date_joined",)
    list_display = ("phone_number", "company_name", "credit_limit", "is_staff", "date_joined")
    list_filter = ("is_staff", "is_active", "industry", "platform")
    search_fields = ("phone_number", "company_name")
    readonly_fields = ("id", "date_joined", "last_login")
    fieldsets = (
        (None, {"fields": ("id", "phone_number", "password")}),
        ("Business", {"fields": ("company_name", "industry", "platform", "credit_limit")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("phone_number", "password1", "password2", "is_staff")}),)
