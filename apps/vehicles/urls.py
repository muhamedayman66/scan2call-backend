from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"", views.VehicleViewSet, basename="vehicle")

urlpatterns = [
    path("guest/location/", views.guest_update_location, name="guest_update_location"),
    path("", include(router.urls)),
]
