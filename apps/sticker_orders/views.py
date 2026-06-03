from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import StickerOrder
from .serializers import StickerOrderSerializer


class StickerOrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StickerOrderSerializer

    def get_queryset(self):
        return StickerOrder.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("VALIDATION ERROR:", serializer.errors)
            return Response(
                {"error": "Validation Failed", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        # Send notification to user about successful order creation
        from apps.notifications.utils import send_fcm_notification

        send_fcm_notification(
            user=self.request.user,
            title="تم استلام طلبك",
            message="لقد تم استلام طلب الملصق الخاص بك بنجاح، سنقوم بمعالجته قريباً.",
            data={"type": "system", "order_id": str(serializer.instance.id)},
            priority="normal",
        )

    @action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None):
        """Update order status (admin only)"""
        if not request.user.is_staff:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        order = self.get_object()
        new_status = request.data.get("status")
        tracking = request.data.get("tracking_number")

        status_changed = new_status and new_status != order.status

        if new_status:
            order.status = new_status
        if tracking:
            order.tracking_number = tracking

        order.save()

        # Send notification on status update
        if status_changed:
            from apps.notifications.utils import send_fcm_notification

            status_map = {
                "processing": "جاري التحضير",
                "shipped": "تم الشحن",
                "delivered": "تم التوصيل",
                "cancelled": "تم الإلغاء",
            }
            ar_status = status_map.get(order.status, order.status)
            send_fcm_notification(
                user=order.user,
                title="تحديث حالة طلب الملصق",
                message=f"تم تغيير حالة طلبك إلى: {ar_status}",
                data={"type": "system", "order_id": str(order.id)},
                priority="normal",
            )

        return Response(StickerOrderSerializer(order).data)
