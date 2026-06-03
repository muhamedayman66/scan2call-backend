from django.contrib import admin

from .models import Chat, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ["sender", "content", "is_read", "created_at"]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "request_info",
        "owner",
        "status",
        "message_count",
        "expires_at",
        "created_at",
    ]
    list_filter = ["status", "created_at", "expires_at"]
    search_fields = ["request__vehicle__plate_number", "owner__full_name"]
    readonly_fields = ["scanner_token", "created_at", "last_activity_at"]
    inlines = [MessageInline]

    fieldsets = (
        ("Chat Info", {"fields": ("request", "owner", "scanner_token", "status")}),
        (
            "Timing",
            {"fields": ("expires_at", "last_activity_at", "created_at", "ended_at")},
        ),
    )

    def request_info(self, obj):
        return f"{obj.request.get_type_display()} - {obj.request.vehicle.plate_number}"

    request_info.short_description = "Request"

    def message_count(self, obj):
        return obj.messages.count()

    message_count.short_description = "Messages"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("request__vehicle", "owner")
            .prefetch_related("messages")
        )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "chat_info",
        "sender",
        "content_preview",
        "is_read",
        "created_at",
    ]
    list_filter = ["sender", "is_read", "created_at"]
    search_fields = ["content", "chat__request__vehicle__plate_number"]
    readonly_fields = ["created_at"]

    def chat_info(self, obj):
        return f"Chat {obj.chat.id}"

    chat_info.short_description = "Chat"

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("chat__request__vehicle")
