import uuid

from django.conf import settings
from django.db import models


class NotificationLog(models.Model):
    TYPE_CHOICES = [
        ("request", "New Request"),
        ("chat", "Chat Message"),
        ("subscription", "Subscription"),
        ("system", "System"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("normal", "Normal"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="normal"
    )

    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField()
    message_ar = models.TextField(null=True, blank=True)

    data = models.JSONField(null=True, blank=True)  # Extra payload

    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)

    fcm_message_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notifications"
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
            models.Index(fields=["type", "priority"]),
        ]

    def __str__(self):
        return f"{self.title} → {self.user.full_name}"
