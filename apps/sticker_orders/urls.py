from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"", views.StickerOrderViewSet, basename="sticker-order")

urlpatterns = [
    path("", include(router.urls)),
]
