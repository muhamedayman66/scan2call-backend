from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.notifications.utils import send_fcm_notification

from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer


class ChatViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer

    def get_queryset(self):
        return (
            Chat.objects.filter(owner=self.request.user)
            .select_related("request__vehicle")
            .prefetch_related("messages")
        )

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        """Get all messages in chat"""
        chat = self.get_object()
        messages = chat.messages.all()

        # Mark owner messages as read
        messages.filter(sender="scanner", is_read=False).update(is_read=True)

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def send_message(self, request, pk=None):
        """Send message as owner"""
        chat = self.get_object()

        if chat.status != "active":
            return Response(
                {"error": "Chat is not active"}, status=status.HTTP_400_BAD_REQUEST
            )

        if chat.is_expired():
            chat.status = "expired"
            chat.save()
            return Response(
                {"error": "Chat has expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        content = request.data.get("content", "").strip()
        attachment = request.FILES.get("attachment")

        if not content and not attachment:
            return Response(
                {"error": "Message content or attachment required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message = Message.objects.create(
            chat=chat, sender="owner", content=content, attachment=attachment
        )

        # Update last activity
        chat.last_activity_at = timezone.now()
        chat.save()

        # Broadcast to websocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{chat.id}",
            {
                "type": "chat_message_broadcast",
                "message": {
                    "id": str(message.id),
                    "sender": message.sender,
                    "content": message.content,
                    "attachment": (
                        message.attachment.url if message.attachment else None
                    ),
                    "created_at": message.created_at.isoformat(),
                },
            },
        )

        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"])
    def end(self, request, pk=None):
        """End chat session"""
        chat = self.get_object()
        chat.end_chat()

        return Response(ChatSerializer(chat).data)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def guest_chat_messages(request, token):
    """Guest chat endpoint - get/send messages using scanner_token"""
    chat = get_object_or_404(Chat, scanner_token=token)

    if chat.status != "active":
        return Response(
            {"error": "Chat is not active", "status": chat.status},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if chat.is_expired():
        chat.status = "expired"
        chat.save()
        return Response(
            {"error": "Chat has expired"}, status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == "GET":
        messages = chat.messages.all()
        # Mark scanner messages as read
        messages.filter(sender="owner", is_read=False).update(is_read=True)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    content = request.data.get("content", "").strip()
    attachment = request.FILES.get("attachment")

    if not content and not attachment:
        return Response(
            {"error": "Message content or attachment required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    message = Message.objects.create(
        chat=chat, sender="scanner", content=content, attachment=attachment
    )

    # Update last activity
    chat.last_activity_at = timezone.now()
    chat.save()

    # Broadcast to websocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"chat_{chat.id}",
        {
            "type": "chat_message_broadcast",
            "message": {
                "id": str(message.id),
                "sender": message.sender,
                "content": message.content,
                "attachment": message.attachment.url if message.attachment else None,
                "created_at": message.created_at.isoformat(),
            },
        },
    )

    # Send silent notification to owner
    send_fcm_notification(
        user=chat.owner,
        title="رسالة جديدة" if chat.owner.language == "ar" else "New Message",
        message=content[:50],
        data={
            "type": "chat_message",
            "chat_id": str(chat.id),
        },
        priority="normal",
    )

    return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
