from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"", views.RequestViewSet, basename="request")

urlpatterns = [
    # Guest endpoints (no auth required)
    path(
        "guest/vehicle/<str:qr_hash>/",
        views.guest_vehicle_info,
        name="guest-vehicle-info",
    ),
    path("guest/requests/", views.guest_create_request, name="guest-create-request"),
    # Authenticated endpoints
    path("", include(router.urls)),
]
