import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import StickerOrder


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            # format: data:image/jpeg;base64,<data>
            try:
                format, imgstr = data.split(";base64,")
                ext = format.split("/")[-1]
                id = uuid.uuid4()
                data = ContentFile(
                    base64.b64decode(imgstr), name=id.urn[9:] + "." + ext
                )
            except Exception:
                pass
        elif isinstance(data, str):
            try:
                decoded_file = base64.b64decode(data)
                data = ContentFile(decoded_file, name=str(uuid.uuid4()) + ".jpg")
            except Exception:
                pass
        return super(Base64ImageField, self).to_internal_value(data)


class StickerOrderSerializer(serializers.ModelSerializer):
    userId = serializers.CharField(source="user.id", read_only=True)
    vehicleId = serializers.CharField(
        source="vehicle_id", allow_null=True, required=False
    )
    deliveryAddress = serializers.CharField(source="delivery_address")
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    fullName = serializers.CharField(
        source="full_name", required=False, allow_null=True, allow_blank=True
    )
    nationalId = serializers.CharField(
        source="national_id", required=False, allow_null=True, allow_blank=True
    )
    vehicleBrand = serializers.CharField(
        source="vehicle_brand", required=False, allow_null=True, allow_blank=True
    )
    vehicleModel = serializers.CharField(
        source="vehicle_model", required=False, allow_null=True, allow_blank=True
    )
    vehicleType = serializers.CharField(
        source="vehicle_type", required=False, allow_null=True, allow_blank=True
    )
    plateNumber = serializers.CharField(
        source="plate_number", required=False, allow_null=True, allow_blank=True
    )
    plateLetters = serializers.CharField(
        source="plate_letters", required=False, allow_null=True, allow_blank=True
    )
    plateNumbers = serializers.CharField(
        source="plate_numbers", required=False, allow_null=True, allow_blank=True
    )
    shippingFee = serializers.DecimalField(
        source="shipping_fee",
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    licensePhoto = Base64ImageField(
        source="license_photo", required=False, allow_null=True
    )
    idFrontPhoto = Base64ImageField(
        source="id_front_photo", required=False, allow_null=True
    )
    idBackPhoto = Base64ImageField(
        source="id_back_photo", required=False, allow_null=True
    )
    totalPrice = serializers.DecimalField(
        source="total_price",
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    rejectionReason = serializers.CharField(
        source="rejection_reason", required=False, allow_null=True, allow_blank=True
    )
    estimatedDeliveryDays = serializers.CharField(
        source="estimated_delivery_days",
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    class Meta:
        model = StickerOrder
        fields = [
            "id",
            "userId",
            "vehicleId",
            "deliveryAddress",
            "status",
            "createdAt",
            "fullName",
            "phone",
            "nationalId",
            "vehicleBrand",
            "vehicleModel",
            "vehicleType",
            "plateNumber",
            "plateLetters",
            "plateNumbers",
            "governorate",
            "shippingFee",
            "licensePhoto",
            "idFrontPhoto",
            "idBackPhoto",
            "totalPrice",
            "rejectionReason",
            "estimatedDeliveryDays",
            "tracking_number",
            "notes",
        ]
        read_only_fields = ["id", "createdAt"]
