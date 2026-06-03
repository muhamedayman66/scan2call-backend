from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from apps.notifications.utils import send_fcm_notification

from .models import Subscription


@shared_task
def send_expiry_reminders():
    """Send reminders for subscriptions expiring soon"""
    three_days = timezone.now() + timedelta(days=3)

    # Subscriptions expiring in 3 days
    expiring_soon = Subscription.objects.filter(
        status="active", expires_at__gte=timezone.now(), expires_at__lte=three_days
    ).select_related("user", "plan")

    for sub in expiring_soon:
        days_left = (sub.expires_at - timezone.now()).days

        send_fcm_notification(
            user=sub.user,
            title="Subscription Expiring Soon",
            message=f"Your {sub.plan.name} plan expires in {days_left} days",
            data={
                "type": "subscription",
                "subscription_id": str(sub.id),
            },
            priority="normal",
        )

    return f"Sent {expiring_soon.count()} expiry reminders"


@shared_task
def auto_renew_subscriptions():
    """Auto-renew subscriptions with auto_renew enabled"""
    expiring_today = Subscription.objects.filter(
        status="active", auto_renew=True, expires_at__date=timezone.now().date()
    ).select_related("plan", "user")

    renewed_count = 0

    for sub in expiring_today:
        # TODO: Charge payment method
        # For now, just extend
        sub.expires_at = timezone.now() + timedelta(days=sub.plan.duration_days)
        sub.save()
        renewed_count += 1

        send_fcm_notification(
            user=sub.user,
            title="Subscription Renewed",
            message=f"Your {sub.plan.name} plan has been renewed",
            data={"type": "subscription"},
            priority="normal",
        )

    return f"Renewed {renewed_count} subscriptions"
