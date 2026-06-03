from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.notifications.models import NotificationLog

User = get_user_model()


class Command(BaseCommand):
    help = "Checks for expiring and expired subscriptions and sends notifications."

    def handle(self, *args, **kwargs):
        now = timezone.now()

        # 1. Check for subscriptions ending in 2 days (48 hours)
        two_days_from_now = now + timedelta(days=2)
        one_day_from_now = now + timedelta(days=1)

        expiring_users = User.objects.filter(
            subscription_status="ACTIVE",
            subscription_plan_id__in=["pro", "premium"],
            subscription_expiry__lte=two_days_from_now,
            subscription_expiry__gt=one_day_from_now,
        )

        for user in expiring_users:
            # Check if we already sent a reminder recently
            recent_reminder = NotificationLog.objects.filter(
                user=user,
                type="subscription",
                title="تذكير: اقترب موعد انتهاء باقتك",
                created_at__gte=now - timedelta(days=3),
            ).exists()

            if not recent_reminder:
                NotificationLog.objects.create(
                    user=user,
                    type="subscription",
                    title="تذكير: اقترب موعد انتهاء باقتك",
                    title_ar="تذكير: اقترب موعد انتهاء باقتك",
                    message=f"باقتك الحالية ({user.subscription_plan_id}) ستنتهي خلال يومين. يرجى التجديد لتجنب توقف الخدمات.",
                    message_ar=f"باقتك الحالية ({user.subscription_plan_id}) ستنتهي خلال يومين. يرجى التجديد لتجنب توقف الخدمات.",
                )
                self.stdout.write(f"Sent reminder to {user.phone}")

        # 2. Check for expired subscriptions
        expired_users = User.objects.filter(
            subscription_status="ACTIVE",
            subscription_plan_id__in=["pro", "premium"],
            subscription_expiry__lte=now,
        )

        for user in expired_users:
            old_plan = user.subscription_plan_id
            user.subscription_status = "EXPIRED"
            user.subscription_plan_id = "free"
            user.save()

            NotificationLog.objects.create(
                user=user,
                type="subscription",
                priority="high",
                title="انتهى اشتراكك",
                title_ar="انتهى اشتراكك",
                message=f"لقد انتهى اشتراكك في باقة ({old_plan}). تم إيقاف الميزات المدفوعة. يرجى التجديد لاستعادة الخدمات.",
                message_ar=f"لقد انتهى اشتراكك في باقة ({old_plan}). تم إيقاف الميزات المدفوعة. يرجى التجديد لاستعادة الخدمات.",
            )
            self.stdout.write(f"Expired subscription for {user.phone}")

        self.stdout.write("Subscription check complete.")
