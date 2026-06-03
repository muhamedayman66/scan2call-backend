from django.contrib import admin

from .models import Invoice, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "price_egp",
        "max_vehicles",
        "duration_days",
        "is_active",
        "sort_order",
    ]
    list_filter = ["is_active", "allow_phone", "location_tracking"]
    search_fields = ["name", "name_ar"]
    ordering = ["sort_order", "price_egp"]

    fieldsets = (
        (
            "Plan Details",
            {"fields": ("name", "name_ar", "description", "description_ar")},
        ),
        ("Pricing", {"fields": ("price_egp", "duration_days")}),
        (
            "Features",
            {
                "fields": (
                    "max_vehicles",
                    "sticker_count",
                    "allow_phone",
                    "location_tracking",
                    "history_days",
                )
            },
        ),
        ("Settings", {"fields": ("is_active", "sort_order")}),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "plan",
        "status",
        "started_at",
        "expires_at",
        "auto_renew",
    ]
    list_filter = ["status", "auto_renew", "started_at", "expires_at"]
    search_fields = ["user__full_name", "user__phone", "plan__name"]
    readonly_fields = ["created_at", "updated_at", "transaction_id"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Subscription", {"fields": ("user", "plan", "status", "auto_renew")}),
        ("Payment", {"fields": ("payment_method", "transaction_id")}),
        (
            "Dates",
            {
                "fields": (
                    "started_at",
                    "expires_at",
                    "created_at",
                    "updated_at",
                    "cancelled_at",
                )
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "plan")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        "invoice_number",
        "subscription_info",
        "amount",
        "currency",
        "payment_status",
        "created_at",
        "paid_at",
    ]
    list_filter = ["payment_status", "currency", "created_at"]
    search_fields = ["invoice_number", "subscription__user__full_name"]
    readonly_fields = ["invoice_number", "created_at"]
    date_hierarchy = "created_at"

    def subscription_info(self, obj):
        return f"{obj.subscription.user.full_name} - {obj.subscription.plan.name}"

    subscription_info.short_description = "Subscription"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("subscription__user", "subscription__plan")
        )
