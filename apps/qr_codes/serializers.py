from rest_framework import serializers

from .models import QRCode


class QRCodeSerializer(serializers.ModelSerializer):
    url = serializers.CharField(read_only=True)
    vehicle_plate = serializers.CharField(source="vehicle.plate_number", read_only=True)

    class Meta:
        model = QRCode
        fields = [
            "id",
            "vehicle",
            "vehicle_plate",
            "code_hash",
            "url",
            "scan_count",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "code_hash", "scan_count", "created_at"]
