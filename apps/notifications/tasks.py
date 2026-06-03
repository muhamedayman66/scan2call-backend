from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import NotificationLog


@shared_task
def cleanup_old_notifications():
    """Delete read notifications older than 90 days"""
    threshold = timezone.now() - timedelta(days=90)

    deleted_count, _ = NotificationLog.objects.filter(
        is_read=True, read_at__lt=threshold
    ).delete()

    return f"Deleted {deleted_count} old notifications"


@shared_task
def send_batch_notifications(user_ids, title, message, notification_type="system"):
    """Send batch notifications to multiple users"""
    from django.contrib.auth import get_user_model

    from .utils import send_fcm_notification

    User = get_user_model()
    users = User.objects.filter(id__in=user_ids)

    sent_count = 0
    for user in users:
        send_fcm_notification(
            user=user,
            title=title,
            message=message,
            data={"type": notification_type},
            priority="normal",
        )
        sent_count += 1

    return f"Sent {sent_count} batch notifications"
