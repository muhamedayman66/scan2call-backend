from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow owners of an object to edit it"""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.owner == request.user


class IsVehicleOwner(permissions.BasePermission):
    """Permission to check if user is the vehicle owner"""

    def has_object_permission(self, request, view, obj):
        return obj.vehicle.owner == request.user


class IsSubscriptionActive(permissions.BasePermission):
    """Permission to check if user has active subscription"""

    def has_permission(self, request, view):
        from django.utils import timezone

        from apps.subscriptions.models import Subscription

        has_active = Subscription.objects.filter(
            user=request.user, status="active", expires_at__gt=timezone.now()
        ).exists()

        return has_active
