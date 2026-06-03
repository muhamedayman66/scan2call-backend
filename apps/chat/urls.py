from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"", views.ChatViewSet, basename="chat")

urlpatterns = [
    path(
        "guest/<uuid:token>/messages/",
        views.guest_chat_messages,
        name="guest-chat-messages",
    ),
    path("", include(router.urls)),
]
