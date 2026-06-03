from django.contrib import admin

from .models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "type",
        "priority",
        "title_preview",
        "is_read",
        "is_sent",
        "created_at",
    ]
    list_filter = ["type", "priority", "is_read", "is_sent", "created_at"]
    search_fields = ["user__full_name", "user__phone", "title", "message"]
    readonly_fields = ["fcm_message_id", "created_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Notification", {"fields": ("user", "type", "priority")}),
        ("Content", {"fields": ("title", "title_ar", "message", "message_ar", "data")}),
        ("Status", {"fields": ("is_read", "is_sent", "fcm_message_id")}),
        ("Timestamps", {"fields": ("created_at", "read_at")}),
    )

    def title_preview(self, obj):
        return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title

    title_preview.short_description = "Title"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")
