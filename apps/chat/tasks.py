from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.utils import timezone

from .models import Chat


@shared_task
def expire_inactive_chats():
    """Auto-expire chats that have passed their expiry time"""
    expired_chats = Chat.objects.filter(status="active", expires_at__lt=timezone.now())

    channel_layer = get_channel_layer()

    for chat in expired_chats:
        chat.status = "expired"
        chat.save()

        # Notify WebSocket clients
        room_group_name = f"chat_{chat.id}"
        async_to_sync(channel_layer.group_send)(
            room_group_name, {"type": "chat_ended", "reason": "expired"}
        )

    return f"Expired {expired_chats.count()} chats"
