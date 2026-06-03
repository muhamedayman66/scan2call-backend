import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.notifications.models import NotificationLog
from apps.notifications.utils import send_fcm_notification

User = get_user_model()
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Checks for subscriptions expiring in 2 days or already expired, and sends notifications.'

    def handle(self, *args, **options):
        now = timezone.now()
        target_2_days = now + timedelta(days=2)
        
        # 1. Check subscriptions expiring in exactly 2 days (within a 24-hour window to avoid spamming)
        # Using date() to match the exact day
        users_expiring_soon = User.objects.filter(
            subscription_status='ACTIVE',
            subscription_expiry__date=target_2_days.date()
        )
        
        for user in users_expiring_soon:
            # Check if we already notified them today to avoid duplicates
            if not NotificationLog.objects.filter(
                user=user, 
                type='subscription', 
                created_at__date=now.date(),
                title__contains='2 days'
            ).exists():
                message_en = "Your subscription is about to expire in 2 days. Please renew to keep your premium features."
                message_ar = "اشتراكك سينتهي خلال يومين. يرجى التجديد للحفاظ على ميزاتك."
                
                send_fcm_notification(
                    user=user,
                    title="Subscription Expiring Soon",
                    message=message_en,
                    data={"type": "subscription"}
                )
                
                NotificationLog.objects.create(
                    user=user,
                    type='subscription',
                    title='Subscription Expiring Soon (2 days)',
                    title_ar='اقتراب انتهاء الاشتراك (يومين)',
                    message=message_en,
                    message_ar=message_ar,
                )
                self.stdout.write(self.style.SUCCESS(f"Sent 2-days expiry warning to {user.phone}"))

        # 2. Check subscriptions that expired today
        users_expired = User.objects.filter(
            subscription_status='ACTIVE',
            subscription_expiry__date__lte=now.date()
        )
        
        for user in users_expired:
            # Update user status to EXPIRED
            user.subscription_status = 'EXPIRED'
            user.save()
            
            message_en = "Your subscription has expired. Please renew your plan."
            message_ar = "لقد انتهى اشتراكك. يرجى تجديد باقتك."
            
            send_fcm_notification(
                user=user,
                title="Subscription Expired",
                message=message_en,
                data={"type": "subscription"}
            )
            
            NotificationLog.objects.create(
                user=user,
                type='subscription',
                title='Subscription Expired',
                title_ar='انتهاء الاشتراك',
                message=message_en,
                message_ar=message_ar,
            )
            self.stdout.write(self.style.WARNING(f"Sent expiry notification and deactivated subscription for {user.phone}"))

        self.stdout.write(self.style.SUCCESS("Finished checking subscriptions."))
