import secrets
import uuid

from django.conf import settings
from django.db import models

from apps.vehicles.models import Vehicle


def generate_qr_hash():
    """Generate a unique 10-character hash for QR code"""
    return secrets.token_urlsafe(8)[:10]


class QRCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.OneToOneField(
        Vehicle, on_delete=models.CASCADE, related_name="qr_code"
    )
    code_hash = models.CharField(
        max_length=12, unique=True, default=generate_qr_hash, db_index=True
    )
    scan_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "qr_codes"
        verbose_name = "QR Code"
        verbose_name_plural = "QR Codes"
        indexes = [
            models.Index(fields=["code_hash", "is_active"]),
        ]

    def __str__(self):
        return f"QR-{self.code_hash} ({self.vehicle.plate_number})"

    @property
    def url(self):
        return f"{settings.BACKEND_URL}/qr/{self.code_hash}/"

    def increment_scan(self):
        self.scan_count += 1
        self.save(update_fields=["scan_count"])
