from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notifications.utils import send_fcm_notification

from .models import Request


@receiver(post_save, sender=Request)
def request_created(sender, instance, created, **kwargs):
    """Send notification when request is created"""
    if created:
        # Determine priority based on request type
        priority_map = {
            "emergency": "critical",
            "accident": "high",
            "move": "high",
            "ticket": "normal",
        }

        priority = priority_map.get(instance.type, "normal")

        # Send FCM notification
        send_fcm_notification(
            user=instance.vehicle.owner,
            title=f"New {instance.get_type_display()} Request",
            message=instance.message
            or f"Someone scanned your {instance.vehicle.plate_number} QR code",
            data={
                "type": "request",
                "request_id": str(instance.id),
                "request_type": instance.type,
                "vehicle_id": str(instance.vehicle.id),
            },
            priority=priority,
        )
