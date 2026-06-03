import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import InstapayPaymentRequest, Invoice, Plan, Subscription


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(
                base64.b64decode(imgstr), name=f"{uuid.uuid4().hex}.{ext}"
            )
        return super().to_internal_value(data)


class PlanSerializer(serializers.ModelSerializer):
    name_localized = serializers.SerializerMethodField()
    description_localized = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = [
            "id",
            "name",
            "name_ar",
            "name_localized",
            "description",
            "description_ar",
            "description_localized",
            "price_egp",
            "duration_days",
            "max_vehicles",
            "sticker_count",
            "allow_phone",
            "location_tracking",
            "history_days",
            "is_active",
        ]

    def get_name_localized(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.name_ar if request.user.language == "ar" else obj.name
        return obj.name

    def get_description_localized(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return (
                obj.description_ar if request.user.language == "ar" else obj.description
            )
        return obj.description


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_info = PlanSerializer(source="plan", read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "plan",
            "plan_info",
            "status",
            "started_at",
            "expires_at",
            "auto_renew",
            "payment_method",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "subscription",
            "amount",
            "currency",
            "invoice_number",
            "payment_status",
            "created_at",
            "paid_at",
        ]


class InstapayPaymentRequestSerializer(serializers.ModelSerializer):
    userId = serializers.CharField(source="user_id", read_only=True)
    planId = serializers.CharField(source="plan_id")
    receiptPhoto = Base64ImageField(source="receipt_photo", required=False)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    rejectionReason = serializers.CharField(
        source="rejection_reason", required=False, allow_blank=True
    )

    class Meta:
        model = InstapayPaymentRequest
        fields = [
            "id",
            "userId",
            "planId",
            "amount",
            "receiptPhoto",
            "status",
            "createdAt",
            "rejectionReason",
        ]
        read_only_fields = ["id"]
