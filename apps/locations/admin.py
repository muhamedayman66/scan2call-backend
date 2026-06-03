from django.contrib import admin

from .models import VehicleLocation


@admin.register(VehicleLocation)
class VehicleLocationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "vehicle",
        "latitude",
        "longitude",
        "address_preview",
        "recorded_at",
    ]
    list_filter = ["recorded_at", "created_at"]
    search_fields = ["vehicle__plate_number", "address"]
    readonly_fields = ["created_at"]
    date_hierarchy = "recorded_at"

    def address_preview(self, obj):
        return (
            obj.address[:50] + "..."
            if obj.address and len(obj.address) > 50
            else obj.address
        )

    address_preview.short_description = "Address"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("vehicle")
