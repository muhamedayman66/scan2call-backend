from rest_framework import serializers

from .models import NotificationLog


class NotificationSerializer(serializers.ModelSerializer):
    title_localized = serializers.SerializerMethodField()
    message_localized = serializers.SerializerMethodField()

    class Meta:
        model = NotificationLog
        fields = [
            "id",
            "type",
            "priority",
            "title",
            "title_ar",
            "title_localized",
            "message",
            "message_ar",
            "message_localized",
            "data",
            "is_read",
            "created_at",
            "read_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_title_localized(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.title_ar if request.user.language == "ar" else obj.title
        return obj.title

    def get_message_localized(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.message_ar if request.user.language == "ar" else obj.message
        return obj.message
