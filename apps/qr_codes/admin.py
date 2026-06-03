from django.contrib import admin
from django.utils.html import format_html

from .models import QRCode


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = [
        "code_hash",
        "vehicle_info",
        "scan_count",
        "is_active",
        "qr_url_link",
        "created_at",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["code_hash", "vehicle__plate_number", "vehicle__owner__full_name"]
    readonly_fields = [
        "code_hash",
        "scan_count",
        "created_at",
        "updated_at",
        "qr_url_link",
    ]

    def vehicle_info(self, obj):
        return f"{obj.vehicle.plate_number} - {obj.vehicle.owner.full_name}"

    vehicle_info.short_description = "Vehicle"

    def qr_url_link(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.url, obj.url)

    qr_url_link.short_description = "QR URL"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("vehicle__owner")
