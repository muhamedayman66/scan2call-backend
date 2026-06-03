from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.qr_codes.models import QRCode

from .models import Vehicle


@receiver(post_save, sender=Vehicle)
def create_qr_code(sender, instance, created, **kwargs):
    """Auto-create QR code when vehicle is created"""
    if created:
        QRCode.objects.get_or_create(vehicle=instance)


@receiver(post_delete, sender=Vehicle)
def delete_qr_code(sender, instance, **kwargs):
    """Delete QR code when vehicle is deleted"""
    if hasattr(instance, "qr_code"):
        instance.qr_code.delete()
