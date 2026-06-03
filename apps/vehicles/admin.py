from django.contrib import admin

from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = [
        "plate_number",
        "owner",
        "brand",
        "model",
        "year",
        "color",
        "is_active",
        "created_at",
    ]
    list_filter = ["brand", "color", "is_active", "year"]
    search_fields = ["plate_number", "owner__full_name", "owner__phone", "model"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Owner", {"fields": ("owner",)}),
        (
            "Vehicle Details",
            {"fields": ("brand", "model", "year", "color", "plate_number")},
        ),
        ("Photos", {"fields": ("photo_1", "photo_2", "photo_3")}),
        ("Settings", {"fields": ("show_phone", "allow_call", "is_active")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("owner")
