import hmac
import secrets

from aiohttp import web


class Authentication:
    """Bearer-token authentication for pyLiveMusic's HTTP API."""

    def __init__(self, auth_key: str | None = None):
        if auth_key is not None and (
            not isinstance(auth_key, str) or not auth_key.strip()
        ):
            raise ValueError("AUTH_KEY must be a non-empty string")

        self.auth_key = auth_key or secrets.token_urlsafe(32)

    def _get_auth_key(self) -> str:
        """Internal compatibility accessor."""
        return self.auth_key

    def _verify(self, request) -> bool:
        provided_key = request.headers.get("Authorization", "")
        expected_key = f"Bearer {self.auth_key}"

        if not provided_key:
            raise web.HTTPUnauthorized(
                text="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not hmac.compare_digest(provided_key, expected_key):
            raise web.HTTPUnauthorized(
                text="Invalid authentication key",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return True

    def _verify_room_access(self, request, room) -> bool:
        """Allow the server API key or this room's viewer credential."""
        provided_key = request.headers.get("Authorization", "")
        if not provided_key:
            raise web.HTTPUnauthorized(
                text="Room access credential required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        accepted = (
            f"Bearer {self.auth_key}",
            f"Bearer {getattr(room, 'viewer_token', '')}",
        )
        if not any(
            hmac.compare_digest(
                provided_key.encode("utf-8"),
                key.encode("utf-8"),
            )
            for key in accepted
            if key != "Bearer "
        ):
            raise web.HTTPUnauthorized(
                text="Invalid room access credential",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return True
