from rest_framework import serializers

from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    qr_code_url = serializers.SerializerMethodField()
    qr_hash = serializers.SerializerMethodField()
    scan_count = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "brand",
            "model",
            "year",
            "color",
            "plate_number",
            "photo_1",
            "photo_2",
            "photo_3",
            "photos",
            "show_phone",
            "allow_call",
            "is_active",
            "qr_code_url",
            "qr_hash",
            "scan_count",
            "latitude",
            "longitude",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_latitude(self, obj):
        loc = obj.locations.first()
        return float(loc.latitude) if loc else None

    def get_longitude(self, obj):
        loc = obj.locations.first()
        return float(loc.longitude) if loc else None

    def get_qr_code_url(self, obj):
        if hasattr(obj, "qr_code"):
            return obj.qr_code.url
        return None

    def get_qr_hash(self, obj):
        if hasattr(obj, "qr_code"):
            return obj.qr_code.code_hash
        return None

    def get_scan_count(self, obj):
        # The frontend calls this scanCount, but we want it to show the number of requests
        return obj.requests.count()

    def get_photos(self, obj):
        photos = []
        for photo in [obj.photo_1, obj.photo_2, obj.photo_3]:
            if photo:
                photos.append(photo)
        return photos


class VehicleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""

    qr_hash = serializers.SerializerMethodField()
    scan_count = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "brand",
            "model",
            "year",
            "color",
            "plate_number",
            "photo_1",
            "qr_hash",
            "scan_count",
            "is_active",
            "latitude",
            "longitude",
        ]

    def get_qr_hash(self, obj):
        if hasattr(obj, "qr_code"):
            return obj.qr_code.code_hash
        return None

    def get_scan_count(self, obj):
        return obj.requests.count()

    def get_latitude(self, obj):
        loc = obj.locations.first()
        return float(loc.latitude) if loc else None

    def get_longitude(self, obj):
        loc = obj.locations.first()
        return float(loc.longitude) if loc else None
