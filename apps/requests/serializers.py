from rest_framework import serializers

from apps.vehicles.serializers import VehicleListSerializer

from .models import Request


class RequestSerializer(serializers.ModelSerializer):
    vehicle_info = VehicleListSerializer(source="vehicle", read_only=True)
    vehicleId = serializers.CharField(source="vehicle_id", read_only=True)
    scannerDeviceId = serializers.CharField(
        source="scanner_device_id", required=False, allow_null=True
    )
    mediaUrl = serializers.FileField(
        source="media_url", required=False, allow_null=True
    )
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    chatId = serializers.SerializerMethodField()

    class Meta:
        model = Request
        fields = [
            "id",
            "vehicleId",
            "vehicle_info",
            "type",
            "status",
            "message",
            "mediaUrl",
            "scannerDeviceId",
            "scanner_location",
            "createdAt",
            "updated_at",
            "resolved_at",
            "chatId",
        ]
        read_only_fields = ["id", "createdAt", "updated_at"]

    def get_chatId(self, obj):
        if hasattr(obj, "chat"):
            return str(obj.chat.id)
        return None


class GuestRequestCreateSerializer(serializers.ModelSerializer):
    qr_hash = serializers.CharField(write_only=True)

    class Meta:
        model = Request
        fields = [
            "qr_hash",
            "type",
            "message",
            "media_url",
            "scanner_device_id",
            "scanner_location",
        ]

    def validate_qr_hash(self, value):
        from apps.qr_codes.models import QRCode

        try:
            qr = QRCode.objects.select_related("vehicle").get(
                code_hash=value, is_active=True
            )
            self.context["vehicle"] = qr.vehicle
            return value
        except QRCode.DoesNotExist:
            raise serializers.ValidationError("Invalid QR code")

    def create(self, validated_data):
        validated_data.pop("qr_hash")
        validated_data["vehicle"] = self.context["vehicle"]
        return super().create(validated_data)


class RequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ["status"]
