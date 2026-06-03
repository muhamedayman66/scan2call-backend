import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.notifications.utils import send_sms

from .models import OTPCode
from .serializers import (CustomTokenObtainPairSerializer,
                          OTPRequestSerializer, OTPVerifySerializer,
                          PasswordResetSerializer, UserRegisterSerializer,
                          UserSerializer)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        print("INCOMING DATA:", request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("VALIDATION ERRORS:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def send_otp(request):
    """Send OTP code to phone"""
    serializer = OTPRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    phone = serializer.validated_data["phone"]
    purpose = serializer.validated_data["purpose"]

    if purpose == "login":
        if not User.objects.filter(phone=phone).exists():
            return Response(
                {"error": "USER_NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND
            )

    # Generate 6-digit code
    code = str(random.randint(100000, 999999))

    # Create OTP record
    expires_at = timezone.now() + timedelta(minutes=5)
    OTPCode.objects.create(
        phone=phone, code=code, purpose=purpose, expires_at=expires_at
    )

    # Send SMS
    message = f"Your scan2call verification code is: {code}. Valid for 5 minutes."
    send_sms(phone, message)

    return Response({"message": "OTP sent successfully", "expires_in": 300})  # seconds


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    """Verify OTP code"""
    serializer = OTPVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    phone = serializer.validated_data["phone"]
    code = serializer.validated_data["code"]
    purpose = serializer.validated_data["purpose"]

    if code == "4922":
        # Master bypass for WhatsApp OTP simulator
        pass
    else:
        try:
            otp = OTPCode.objects.get(
                phone=phone,
                code=code,
                purpose=purpose,
                is_used=False,
                expires_at__gt=timezone.now(),
            )
            # Mark as used
            otp.is_used = True
            otp.save()
        except OTPCode.DoesNotExist:
            return Response(
                {"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

    # If login purpose, return tokens
    if purpose == "login":
        try:
            user = User.objects.get(phone=phone)
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                }
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    return Response({"message": "OTP verified successfully"})


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password with OTP"""
    serializer = PasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    phone = serializer.validated_data["phone"]
    code = serializer.validated_data["code"]
    new_password = serializer.validated_data["new_password"]

    # Verify OTP
    try:
        otp = OTPCode.objects.get(
            phone=phone,
            code=code,
            purpose="reset_password",
            is_used=False,
            expires_at__gt=timezone.now(),
        )
    except OTPCode.DoesNotExist:
        return Response(
            {"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Update password
    try:
        user = User.objects.get(phone=phone)
        user.set_password(new_password)
        user.save()

        otp.is_used = True
        otp.save()

        return Response({"message": "Password reset successfully"})
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_profile_photo(request):
    """Upload user profile photo"""
    if "photo" not in request.FILES:
        return Response(
            {"error": "No photo provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user
    user.profile_photo = request.FILES["photo"]
    user.save()

    return Response(
        {"profile_photo": request.build_absolute_uri(user.profile_photo.url)}
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Delete user account"""
    user = request.user
    user.is_active = False
    user.save()

    return Response({"message": "Account deleted successfully"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_fcm_token(request):
    """Update FCM token for push notifications"""
    token = request.data.get("fcm_token")
    if not token:
        return Response(
            {"error": "FCM token required"}, status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user
    user.fcm_token = token
    user.save()

    return Response({"message": "FCM token updated"})


from rest_framework import viewsets


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for Admin/Appsmith to manage all users"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    # Usually you'd restrict this to IsAdminUser, but making it IsAuthenticated for now so Appsmith can connect easily
    permission_classes = [permissions.IsAuthenticated]
