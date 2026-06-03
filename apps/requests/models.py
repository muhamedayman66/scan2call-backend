import uuid

from django.conf import settings
from django.db import models

from apps.vehicles.models import Vehicle


class Request(models.Model):
    REQUEST_TYPE_CHOICES = [
        ("move", "Move Please"),
        ("emergency", "Emergency"),
        ("ticket", "Traffic Ticket"),
        ("accident", "Accident"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("acknowledged", "Acknowledged"),
        ("resolved", "Resolved"),
        ("dismissed", "Dismissed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="requests"
    )

    type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    message = models.TextField(blank=True)
    media_url = models.FileField(upload_to="request_media/", null=True, blank=True)

    # Scanner info (anonymous)
    scanner_device_id = models.CharField(max_length=100, null=True, blank=True)
    scanner_ip = models.GenericIPAddressField(null=True, blank=True)
    scanner_location = models.JSONField(null=True, blank=True)  # {lat, lng}

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "requests"
        verbose_name = "Request"
        verbose_name_plural = "Requests"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["vehicle", "status", "-created_at"]),
            models.Index(fields=["type", "status"]),
        ]

    def __str__(self):
        return (
            f"{self.get_type_display()} - {self.vehicle.plate_number} ({self.status})"
        )
