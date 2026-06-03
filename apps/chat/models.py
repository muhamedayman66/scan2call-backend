import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.requests.models import Request


class Chat(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("ended", "Ended"),
        ("expired", "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.OneToOneField(
        Request, on_delete=models.CASCADE, related_name="chat"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owner_chats"
    )
    scanner_token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    expires_at = models.DateTimeField()
    last_activity_at = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "chats"
        verbose_name = "Chat"
        verbose_name_plural = "Chats"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "expires_at"]),
            models.Index(fields=["scanner_token"]),
        ]

    def __str__(self):
        return f"Chat {self.id} - {self.request.vehicle.plate_number}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(
                minutes=settings.CHAT_EXPIRY_MINUTES
            )
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def end_chat(self):
        self.status = "ended"
        self.ended_at = timezone.now()
        self.save(update_fields=["status", "ended_at"])


class Message(models.Model):
    SENDER_CHOICES = [
        ("owner", "Owner"),
        ("scanner", "Scanner"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    attachment = models.ImageField(upload_to="chat_attachments/", null=True, blank=True)
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "messages"
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["chat", "created_at"]),
            models.Index(fields=["is_read"]),
        ]

    def __str__(self):
        return f"{self.sender} @ {self.created_at}"
