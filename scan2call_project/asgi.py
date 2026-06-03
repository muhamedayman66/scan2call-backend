import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.wsgi import get_wsgi_application
from asgiref.wsgi import WsgiToAsgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scan2call_project.settings")

django_wsgi_app = get_wsgi_application()
django_asgi_app = WsgiToAsgi(django_wsgi_app)

from apps.chat.middleware import JWTAuthMiddleware
from apps.chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        ),
    }
)
