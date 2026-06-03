from rest_framework import serializers

from .models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    chatId = serializers.CharField(source="chat_id", read_only=True)
    isRead = serializers.BooleanField(source="is_read", required=False)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "chatId",
            "sender",
            "content",
            "attachment",
            "isRead",
            "createdAt",
        ]
        read_only_fields = ["id", "createdAt"]


class ChatSerializer(serializers.ModelSerializer):
    requestId = serializers.CharField(source="request_id", read_only=True)
    ownerId = serializers.CharField(source="owner_id", read_only=True)
    scannerToken = serializers.CharField(source="scanner_token", read_only=True)
    expiresAt = serializers.DateTimeField(source="expires_at", read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = [
            "id",
            "requestId",
            "ownerId",
            "scannerToken",
            "status",
            "expiresAt",
            "messages",
        ]
        read_only_fields = ["id", "scannerToken"]

    def get_time_remaining(self, obj):
        from django.utils import timezone

        if obj.status == "active":
            remaining = obj.expires_at - timezone.now()
            return max(0, int(remaining.total_seconds()))
        return 0
