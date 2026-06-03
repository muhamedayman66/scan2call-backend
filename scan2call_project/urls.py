from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from apps.vehicles.views import guest_tracking_page_view

# Auto-register all models for admin access
models = apps.get_models()
for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
urlpatterns = [
    path("admin/", admin.site.urls),
    # API endpoints
    path("api/auth/", include("apps.users.urls")),
    path("api/vehicles/", include("apps.vehicles.urls")),
    path("api/requests/", include("apps.requests.urls")),
    path("api/chat/", include("apps.chat.urls")),
    path("api/", include("apps.subscriptions.urls")),
    path("api/stickers/", include("apps.sticker_orders.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    # Guest pages
    path("qr/", include("apps.qr_codes.urls")),
    path("track/<uuid:token>/", guest_tracking_page_view, name="guest-track"),
    # Health check
    path("health/", lambda request: JsonResponse({"status": "ok"})),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
