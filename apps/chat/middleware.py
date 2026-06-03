from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Parse query string
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)

        # Try JWT token first
        token = query_params.get("token", [None])[0]
        if token:
            user = await self.get_user_from_token(token)
            if user:
                scope["user"] = user

        # Try scanner token
        scanner_token = query_params.get("scanner_token", [None])[0]
        if scanner_token:
            scope["scanner_token"] = scanner_token

        if "user" not in scope:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token_string):
        try:
            token = AccessToken(token_string)
            user_id = token.payload.get("user_id")
            return User.objects.get(id=user_id)
        except Exception:
            return None
