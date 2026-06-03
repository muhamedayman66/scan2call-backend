import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Plan(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    description = models.TextField()
    description_ar = models.TextField()

    price_egp = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(default=30)

    max_vehicles = models.IntegerField()
    sticker_count = models.IntegerField(default=1)
    allow_phone = models.BooleanField(default=False)
    location_tracking = models.BooleanField(default=False)
    history_days = models.IntegerField(default=30)

    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "plans"
        verbose_name = "Plan"
        verbose_name_plural = "Plans"
        ordering = ["sort_order", "price_egp"]

    def __str__(self):
        return f"{self.name} - {self.price_egp} EGP"


class Subscription(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
        ("pending", "Pending Payment"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.PROTECT, related_name="subscriptions"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    started_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)

    payment_method = models.CharField(max_length=50, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "subscriptions"
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["expires_at", "status"]),
        ]

    def __str__(self):
        return f"{self.user.full_name} - {self.plan.name} ({self.status})"

    @property
    def is_active(self):
        return self.status == "active" and self.expires_at > timezone.now()


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name="invoices"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="EGP")

    invoice_number = models.CharField(max_length=50, unique=True)
    payment_status = models.CharField(max_length=20, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "invoices"
        ordering = ["-created_at"]


class InstapayPaymentRequest(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    id = models.CharField(
        primary_key=True, max_length=50
    )  # To match prototype format 'pay-123'
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instapay_payments",
    )
    plan_id = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    receipt_photo = models.ImageField(upload_to="receipts/", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    rejection_reason = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "instapay_payments"
        verbose_name = "Instapay Payment Request"
        verbose_name_plural = "Instapay Payment Requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.id} - {self.user.full_name} ({self.status})"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if not is_new:
            try:
                old_obj = InstapayPaymentRequest.objects.get(pk=self.pk)
                if old_obj.status != "APPROVED" and self.status == "APPROVED":
                    from datetime import timedelta

                    from apps.notifications.utils import send_fcm_notification
                    from apps.notifications.models import NotificationLog

                    user = self.user
                    user.subscription_plan_id = self.plan_id
                    user.subscription_status = "ACTIVE"
                    user.subscription_started_at = timezone.now()
                    user.subscription_expiry = timezone.now() + timedelta(days=30)
                    user.save()

                    title_en = "Subscription Activated"
                    title_ar = "تم تفعيل باقتك بنجاح"
                    msg_en = f"Your payment has been approved. Your {self.plan_id} plan is now active."
                    msg_ar = f"لقد تمت الموافقة على طلب الدفع الخاص بك. باقة {self.plan_id} مفعلة الآن."

                    NotificationLog.objects.create(
                        user=user,
                        type="subscription",
                        title=title_en,
                        title_ar=title_ar,
                        message=msg_en,
                        message_ar=msg_ar,
                        priority="high"
                    )
                    send_fcm_notification(
                        user=user,
                        title=title_ar,
                        message=msg_ar,
                        data={"type": "subscription"}
                    )
                    
                elif old_obj.status != "REJECTED" and self.status == "REJECTED":
                    from apps.notifications.utils import send_fcm_notification
                    from apps.notifications.models import NotificationLog

                    title_en = "Payment Request Rejected"
                    title_ar = "تم رفض طلب الدفع"
                    msg_en = f"Your InstaPay payment request was rejected. Reason: {self.rejection_reason or 'None provided'}."
                    msg_ar = f"تم رفض طلب الدفع الخاص بك. السبب: {self.rejection_reason or 'غير محدد'}."

                    NotificationLog.objects.create(
                        user=self.user,
                        type="subscription",
                        title=title_en,
                        title_ar=title_ar,
                        message=msg_en,
                        message_ar=msg_ar,
                        priority="high"
                    )
                    send_fcm_notification(
                        user=self.user,
                        title=title_ar,
                        message=msg_ar,
                        data={"type": "subscription"}
                    )
            except InstapayPaymentRequest.DoesNotExist:
                pass
        super().save(*args, **kwargs)
