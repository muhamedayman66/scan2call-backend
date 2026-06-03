from django.contrib import admin

from .models import Request


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ["id", "vehicle_info", "type", "status", "has_media", "created_at"]
    list_filter = ["type", "status", "created_at"]
    search_fields = ["vehicle__plate_number", "vehicle__owner__full_name", "message"]
    readonly_fields = ["created_at", "updated_at", "scanner_ip"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Vehicle", {"fields": ("vehicle",)}),
        ("Request Details", {"fields": ("type", "status", "message", "media_url")}),
        (
            "Scanner Info",
            {
                "fields": ("scanner_device_id", "scanner_ip", "scanner_location"),
                "classes": ("collapse",),
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at", "resolved_at")}),
    )

    def vehicle_info(self, obj):
        return f"{obj.vehicle.plate_number} - {obj.vehicle.owner.full_name}"

    vehicle_info.short_description = "Vehicle"

    def has_media(self, obj):
        return bool(obj.media_url)

    has_media.boolean = True
    has_media.short_description = "Media"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("vehicle__owner")
