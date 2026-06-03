from django.contrib import admin

from .models import StickerOrder


@admin.register(StickerOrder)
class StickerOrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "vehicle", "status", "governorate", "created_at"]
    list_filter = ["status", "created_at", "delivered_at"]
    search_fields = [
        "user__full_name",
        "vehicle__plate_number",
        "tracking_number",
        "governorate",
        "plate_number",
    ]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Order Info", {"fields": ("user", "vehicle", "status")}),
        (
            "Delivery Details",
            {
                "fields": (
                    "full_name",
                    "phone",
                    "national_id",
                    "delivery_address",
                    "governorate",
                )
            },
        ),
        (
            "Vehicle Details",
            {
                "fields": (
                    "vehicle_brand",
                    "vehicle_model",
                    "vehicle_type",
                    "plate_number",
                    "plate_letters",
                    "plate_numbers",
                )
            },
        ),
        (
            "Pricing & Shipping",
            {
                "fields": (
                    "shipping_fee",
                    "total_price",
                    "estimated_delivery_days",
                    "tracking_number",
                    "notes",
                )
            },
        ),
        ("Documents", {"fields": ("license_photo", "id_front_photo", "id_back_photo")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at", "shipped_at", "delivered_at")},
        ),
    )

    actions = ["mark_as_shipped", "mark_as_delivered"]

    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone

        queryset.update(status="shipped", shipped_at=timezone.now())

    mark_as_shipped.short_description = "Mark selected as shipped"

    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone

        queryset.update(status="delivered", delivered_at=timezone.now())

    mark_as_delivered.short_description = "Mark selected as delivered"
