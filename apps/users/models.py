import uuid

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError(_("Phone number is required"))
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("ar", "Arabic"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone = models.CharField(
        validators=[phone_regex], max_length=17, unique=True, db_index=True
    )
    email = models.EmailField(unique=True, null=True, blank=True, db_index=True)
    full_name = models.CharField(max_length=255)
    profile_photo = models.TextField(null=True, blank=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default="en")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    fcm_token = models.CharField(max_length=255, null=True, blank=True)

    # Preferences & Subscription (matching prototype)
    show_phone_in_requests = models.BooleanField(default=False)
    subscription_plan_id = models.CharField(max_length=50, default="free")
    subscription_status = models.CharField(max_length=20, default="ACTIVE")
    subscription_expiry = models.DateTimeField(null=True, blank=True)
    subscription_started_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "users"
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=["phone", "is_active"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

    @property
    def first_name(self):
        return self.full_name.split()[0] if self.full_name else ""


class OTPCode(models.Model):
    OTP_PURPOSE_CHOICES = [
        ("register", "Registration"),
        ("login", "Login"),
        ("reset_password", "Reset Password"),
        ("verify_phone", "Verify Phone"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=17, db_index=True)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=OTP_PURPOSE_CHOICES)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "otp_codes"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone", "code", "is_used"]),
        ]

    def __str__(self):
        return f"{self.phone} - {self.code} ({self.purpose})"
