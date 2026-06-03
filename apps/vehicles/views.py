from datetime import timedelta
from io import BytesIO

import qrcode
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.locations.models import TrackingSession
from apps.locations.serializers import VehicleLocationSerializer
from apps.notifications.utils import send_fcm_notification
from apps.notifications.models import NotificationLog

from .models import Vehicle
from .serializers import VehicleListSerializer, VehicleSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return VehicleListSerializer
        return VehicleSerializer

    def get_queryset(self):
        return Vehicle.objects.filter(owner=self.request.user).select_related("qr_code")

    def perform_create(self, serializer):
        user = self.request.user
        limit = 1
        if user.subscription_plan_id == "pro":
            limit = 2
        elif user.subscription_plan_id == "premium":
            limit = 5

        current_count = Vehicle.objects.filter(owner=user).count()
        if current_count >= limit:
            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                {"error": f"Vehicle limit ({limit}) reached for your current plan."}
            )

        vehicle = serializer.save(owner=user)

        # Vehicle Added Notification
        title_en = "Vehicle Added"
        title_ar = "تم إضافة مركبة"
        msg_en = f"Your vehicle {vehicle.brand} {vehicle.model} has been added successfully."
        msg_ar = f"تم إضافة سيارتك {vehicle.brand} {vehicle.model} بنجاح."
        
        NotificationLog.objects.create(
            user=user,
            type="system",
            title=title_en,
            title_ar=title_ar,
            message=msg_en,
            message_ar=msg_ar
        )
        send_fcm_notification(
            user=user,
            title=title_en,
            message=msg_en,
            data={"type": "system"}
        )

    @action(detail=True, methods=["get"])
    def qr_code(self, request, pk=None):
        """Get QR code image for vehicle"""
        vehicle = self.get_object()

        if not hasattr(vehicle, "qr_code"):
            return Response(
                {"error": "QR code not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Generate QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(vehicle.qr_code.url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Return as image
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return HttpResponse(buffer.getvalue(), content_type="image/png")

    @action(detail=True, methods=["post", "get"])
    def location(self, request, pk=None):
        """Update or get vehicle location"""
        vehicle = self.get_object()

        if request.method == "POST":
            print(f"Location POST Data: {request.data}")
            serializer = VehicleLocationSerializer(data=request.data)
            if not serializer.is_valid():
                print(f"Location Serializer Errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(vehicle=vehicle)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # GET - return last location
        last_location = vehicle.locations.first()
        if last_location:
            serializer = VehicleLocationSerializer(last_location)
            return Response(serializer.data)

        return Response(
            {"message": "No location data"}, status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True, methods=["get"])
    def location_history(self, request, pk=None):
        """Get location history for vehicle"""
        vehicle = self.get_object()
        locations = vehicle.locations.all()[:50]  # Last 50 locations
        serializer = VehicleLocationSerializer(locations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def generate_tracking_link(self, request, pk=None):
        """Generate a temporary tracking session token for a guest borrower"""
        vehicle = self.get_object()

        if vehicle.owner.subscription_status != "ACTIVE":
            return Response(
                {"error": "Subscription inactive. Tracking disabled."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Deactivate old active sessions
        TrackingSession.objects.filter(vehicle=vehicle, is_active=True).update(
            is_active=False
        )

        # Create a new session valid for 24 hours
        session = TrackingSession.objects.create(
            vehicle=vehicle, expires_at=timezone.now() + timedelta(hours=24)
        )

        # Return a web link instead of deep link
        link = request.build_absolute_uri(f"/track/{session.id}/")
        return Response(
            {"token": str(session.id), "link": link, "expires_at": session.expires_at}
        )


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def guest_update_location(request):
    """Guest endpoint to update vehicle location via tracking token"""
    token = request.data.get("token")
    if not token:
        return Response(
            {"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        session = TrackingSession.objects.get(id=token, is_active=True)
        if session.expires_at and session.expires_at < timezone.now():
            session.is_active = False
            session.save()
            return Response(
                {"error": "Tracking session expired"}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = VehicleLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(vehicle=session.vehicle)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except TrackingSession.DoesNotExist:
        return Response(
            {"error": "Invalid or inactive tracking token"},
            status=status.HTTP_404_NOT_FOUND,
        )


def guest_tracking_page_view(request, token):
    """Render the web-based guest live tracking page"""
    try:
        session = TrackingSession.objects.get(id=token, is_active=True)
        if session.expires_at and session.expires_at < timezone.now():
            session.is_active = False
            session.save()
            return render(
                request,
                "guest/error.html",
                {"error_message": "Tracking session has expired."},
            )

        return render(
            request,
            "guest/tracking.html",
            {
                "token": token,
                "vehicle_name": f"{session.vehicle.brand} {session.vehicle.model}",
                "vehicle_plate": session.vehicle.plate_number,
            },
        )
    except TrackingSession.DoesNotExist:
        return render(
            request,
            "guest/error.html",
            {"error_message": "Invalid or inactive tracking token."},
        )
