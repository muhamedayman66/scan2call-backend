from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import NotificationLog
from .serializers import NotificationSerializer


class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        queryset = NotificationLog.objects.filter(user=self.request.user)

        # Filter by type
        notification_type = self.request.query_params.get("type")
        if notification_type:
            queryset = queryset.filter(type=notification_type)

        # Filter by read status
        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == "true")

        # Filter by exclude_type
        exclude_type = self.request.query_params.get("exclude_type")
        if exclude_type:
            queryset = queryset.exclude(type=exclude_type)

        return queryset.order_by("-created_at")

    @action(detail=True, methods=["patch"])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()

        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        NotificationLog.objects.filter(user=request.user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )

        return Response({"message": "All notifications marked as read"})

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """Get unread notification count"""
        count = NotificationLog.objects.filter(user=request.user, is_read=False).count()

        return Response({"unread_count": count})
