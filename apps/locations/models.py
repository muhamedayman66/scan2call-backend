import uuid

from django.db import models

from apps.vehicles.models import Vehicle


class VehicleLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="locations"
    )

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.CharField(max_length=255, null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)

    recorded_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vehicle_locations"
        verbose_name = "Vehicle Location"
        verbose_name_plural = "Vehicle Locations"
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["vehicle", "-recorded_at"]),
        ]

    def __str__(self):
        return f"{self.vehicle.plate_number} @ {self.recorded_at}"


class TrackingSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="tracking_sessions"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tracking_sessions"
        verbose_name = "Tracking Session"
        verbose_name_plural = "Tracking Sessions"

    def __str__(self):
        return f"Tracking for {self.vehicle.plate_number} (Active: {self.is_active})"
