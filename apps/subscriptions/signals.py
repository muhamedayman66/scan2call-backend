import uuid

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Invoice, Subscription


@receiver(pre_save, sender=Invoice)
def generate_invoice_number(sender, instance, **kwargs):
    """Generate unique invoice number"""
    if not instance.invoice_number:
        instance.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"


@receiver(post_save, sender=Subscription)
def subscription_status_changed(sender, instance, created, **kwargs):
    """Handle subscription status changes"""
    if not created and instance.status == "active":
        # Notify user of activation
        from apps.notifications.utils import send_fcm_notification

        send_fcm_notification(
            user=instance.user,
            title="Subscription Activated",
            message=f"Your {instance.plan.name} plan is now active!",
            data={"type": "subscription", "subscription_id": str(instance.id)},
            priority="normal",
        )
