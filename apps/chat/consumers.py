import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from .models import Chat, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_group_name = f"chat_{self.chat_id}"
        self.user = self.scope.get("user")
        self.is_owner = False
        self.is_scanner = False

        # Verify access
        chat = await self.get_chat()
        if not chat:
            await self.close(code=4004)
            return

        # Check if user is owner or has scanner token
        if self.user and self.user.is_authenticated:
            if str(chat["owner_id"]) == str(self.user.id):
                self.is_owner = True

        scanner_token = self.scope.get("scanner_token")
        if scanner_token and scanner_token == chat["scanner_token"]:
            self.is_scanner = True

        if not (self.is_owner or self.is_scanner):
            await self.close(code=4003)
            return

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # Send initial chat state
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat_status",
                    "status": chat["status"],
                    "expires_at": chat["expires_at"],
                }
            )
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "chat_message":
            content = data.get("content", "").strip()
            if not content:
                return

            # Determine sender
            sender = "owner" if self.is_owner else "scanner"

            # Save message
            message = await self.save_message(content, sender)
            if not message:
                return

            # Broadcast to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message_broadcast",
                    "message": {
                        "id": str(message["id"]),
                        "sender": message["sender"],
                        "content": message["content"],
                        "attachment": message["attachment"],
                        "created_at": message["created_at"],
                    },
                },
            )

        elif message_type == "typing":
            # Broadcast typing indicator
            sender = "owner" if self.is_owner else "scanner"
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_broadcast",
                    "sender": sender,
                    "is_typing": data.get("is_typing", False),
                },
            )

    async def chat_message_broadcast(self, event):
        await self.send(
            text_data=json.dumps({"type": "message", "message": event["message"]})
        )

    async def typing_broadcast(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "typing",
                    "sender": event["sender"],
                    "is_typing": event["is_typing"],
                }
            )
        )

    async def chat_ended(self, event):
        await self.send(
            text_data=json.dumps(
                {"type": "chat_ended", "reason": event.get("reason", "ended")}
            )
        )

    @database_sync_to_async
    def get_chat(self):
        try:
            chat = Chat.objects.select_related("owner").get(id=self.chat_id)
            return {
                "id": str(chat.id),
                "owner_id": str(chat.owner.id),
                "scanner_token": str(chat.scanner_token),
                "status": chat.status,
                "expires_at": chat.expires_at.isoformat(),
            }
        except Chat.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, content, sender):
        try:
            chat = Chat.objects.get(id=self.chat_id, status="active")

            if chat.is_expired():
                chat.status = "expired"
                chat.save()
                return None

            message = Message.objects.create(chat=chat, sender=sender, content=content)

            # Update last activity
            chat.last_activity_at = timezone.now()
            chat.save()

            return {
                "id": message.id,
                "sender": message.sender,
                "content": message.content,
                "attachment": message.attachment.url if message.attachment else None,
                "created_at": message.created_at.isoformat(),
            }
        except Chat.DoesNotExist:
            return None
