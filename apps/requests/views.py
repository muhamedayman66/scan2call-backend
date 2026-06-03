from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.chat.models import Chat
from apps.notifications.utils import send_fcm_notification
from apps.qr_codes.models import QRCode
from apps.vehicles.serializers import VehicleListSerializer

from .models import Request
from .serializers import (GuestRequestCreateSerializer, RequestSerializer,
                          RequestUpdateSerializer)


@api_view(["GET"])
@permission_classes([AllowAny])
def guest_vehicle_info(request, qr_hash):
    """Get vehicle info for guest (scanner)"""
    qr = get_object_or_404(QRCode, code_hash=qr_hash, is_active=True)
    qr.increment_scan()

    vehicle = qr.vehicle
    serializer = VehicleListSerializer(vehicle, context={"request": request})

    return Response(
        {
            "vehicle": serializer.data,
            "owner_name": vehicle.owner.first_name,
            "owner_photo": (
                request.build_absolute_uri(vehicle.owner.profile_photo.url)
                if vehicle.owner.profile_photo
                else None
            ),
            "show_phone": vehicle.show_phone,
            "allow_call": vehicle.allow_call,
            "owner_phone": vehicle.owner.phone if vehicle.show_phone else None,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="5/10m", method="POST")
def guest_create_request(request):
    """Create request from guest (scanner)"""
    serializer = GuestRequestCreateSerializer(
        data=request.data, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)

    # Create request
    request_obj = serializer.save(scanner_ip=request.META.get("REMOTE_ADDR"))

    # Create chat session
    chat = Chat.objects.create(request=request_obj, owner=request_obj.vehicle.owner)

    owner = request_obj.vehicle.owner
    type_ar_map = {
        "move": "تحريك سيارة",
        "emergency": "طوارئ",
        "ticket": "مخالفة",
        "accident": "حادث",
    }

    if owner.language == "ar":
        type_str = type_ar_map.get(request_obj.type, request_obj.get_type_display())
        title = f"طلب {type_str} جديد"
        message = f"تم مسح كود QR لسيارتك {request_obj.vehicle.plate_number}"
    else:
        title = f"New {request_obj.get_type_display()} Request"
        message = f"Someone scanned your {request_obj.vehicle.plate_number} QR code"

    # Send push notification
    send_fcm_notification(
        user=owner,
        title=title,
        message=message,
        data={
            "type": "request",
            "request_id": str(request_obj.id),
            "chat_id": str(chat.id),
        },
        priority="high" if request_obj.type in ["emergency", "accident"] else "normal",
    )

    return Response(
        {
            "request": RequestSerializer(request_obj).data,
            "chat_token": str(chat.scanner_token),
            "chat_id": str(chat.id),
        },
        status=status.HTTP_201_CREATED,
    )


class RequestViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RequestSerializer

    def get_queryset(self):
        queryset = (
            Request.objects.filter(vehicle__owner=self.request.user)
            .select_related("vehicle")
            .order_by("-created_at")
        )

        # Filters
        request_type = self.request.query_params.get("type")
        request_status = self.request.query_params.get("status")

        if request_type:
            queryset = queryset.filter(type=request_type)
        if request_status:
            queryset = queryset.filter(status=request_status)

        return queryset

    @action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None):
        """Update request status"""
        request_obj = self.get_object()
        old_status = request_obj.status
        serializer = RequestUpdateSerializer(
            request_obj, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        new_status = request_obj.status
        if old_status != "resolved" and new_status == "resolved":
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer

            from apps.chat.models import Chat

            # Find the active chat for this request
            active_chat = Chat.objects.filter(
                request=request_obj, status="active"
            ).first()
            if active_chat:
                active_chat.status = "expired"
                active_chat.save()

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"chat_{active_chat.id}",
                    {"type": "chat_ended", "reason": "resolved"},
                )

        return Response(RequestSerializer(request_obj).data)

    @action(detail=False, methods=["get"])
    def history(self, request):
        """Get request history with filters"""
        queryset = self.get_queryset()

        # Date range filter
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        if from_date:
            queryset = queryset.filter(created_at__gte=from_date)
        if to_date:
            queryset = queryset.filter(created_at__lte=to_date)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
