from rest_framework import serializers

from .models import VehicleLocation


class VehicleLocationSerializer(serializers.ModelSerializer):
    recorded_at = serializers.DateTimeField(required=False)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

    class Meta:
        model = VehicleLocation
        fields = [
            "id",
            "vehicle",
            "latitude",
            "longitude",
            "address",
            "accuracy",
            "recorded_at",
            "created_at",
        ]
        read_only_fields = ["id", "vehicle", "created_at"]

    def create(self, validated_data):
        if "recorded_at" not in validated_data:
            from django.utils import timezone

            validated_data["recorded_at"] = timezone.now()
        return super().create(validated_data)
