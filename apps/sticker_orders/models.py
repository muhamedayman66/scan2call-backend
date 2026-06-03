import uuid

from django.conf import settings
from django.db import models

from apps.vehicles.models import Vehicle


class StickerOrder(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("PROCESSING", "Processing"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
        ("REJECTED", "Rejected"),
        ("CANCELLED", "Cancelled"),
    ]

    id = models.CharField(
        primary_key=True, max_length=50, default=uuid.uuid4
    )  # To match 'ord-123' or uuid
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sticker_orders",
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sticker_orders",
    )

    delivery_address = models.TextField()

    # Detailed fields from prototype
    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    national_id = models.CharField(max_length=20, null=True, blank=True)
    vehicle_brand = models.CharField(max_length=100, null=True, blank=True)
    vehicle_model = models.CharField(max_length=100, null=True, blank=True)
    vehicle_type = models.CharField(max_length=100, null=True, blank=True)
    plate_number = models.CharField(max_length=50, null=True, blank=True)
    plate_letters = models.CharField(max_length=20, null=True, blank=True)
    plate_numbers = models.CharField(max_length=20, null=True, blank=True)
    governorate = models.CharField(max_length=100, null=True, blank=True)

    shipping_fee = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    license_photo = models.ImageField(
        upload_to="sticker_orders/licenses/", null=True, blank=True
    )
    id_front_photo = models.ImageField(
        upload_to="sticker_orders/id_front/", null=True, blank=True
    )
    id_back_photo = models.ImageField(
        upload_to="sticker_orders/id_back/", null=True, blank=True
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    rejection_reason = models.TextField(null=True, blank=True)
    estimated_delivery_days = models.CharField(max_length=50, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "sticker_orders"
        verbose_name = "Sticker Order"
        verbose_name_plural = "Sticker Orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"Order {self.id} - {self.user.full_name} ({self.status})"
