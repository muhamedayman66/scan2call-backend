from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import OTPCode

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "email",
            "full_name",
            "profile_photo",
            "language",
            "is_verified",
            "created_at",
            "show_phone_in_requests",
            "subscription_plan_id",
            "subscription_status",
            "subscription_expiry",
            "subscription_started_at",
        ]
        read_only_fields = ["id", "is_verified", "created_at"]


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "phone",
            "email",
            "full_name",
            "password",
            "password_confirm",
            "language",
            "profile_photo",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class OTPRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=17)
    purpose = serializers.ChoiceField(choices=OTPCode.OTP_PURPOSE_CHOICES)


class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=17)
    code = serializers.CharField(max_length=6)
    purpose = serializers.ChoiceField(choices=OTPCode.OTP_PURPOSE_CHOICES)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "phone"

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class PasswordResetSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=17)
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs
