from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, OTPCode


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = [
        "phone",
        "full_name",
        "email",
        "is_verified",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_verified", "is_active", "is_staff", "language"]
    search_fields = ["phone", "full_name", "email"]
    ordering = ["-created_at"]

    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        (
            _("Personal info"),
            {"fields": ("full_name", "email", "profile_photo", "language")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_verified",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "full_name", "email", "password1", "password2"),
            },
        ),
    )

    readonly_fields = ["created_at", "updated_at"]


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ["phone", "code", "purpose", "is_used", "expires_at", "created_at"]
    list_filter = ["purpose", "is_used", "created_at"]
    search_fields = ["phone", "code"]
    readonly_fields = ["created_at"]

    def has_add_permission(self, request):
        return False
