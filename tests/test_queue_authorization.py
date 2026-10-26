import unittest
from types import SimpleNamespace

from aiohttp import web

from _api.queue import get_room_for_control
from _core._core_func._auth._auth import Authentication


class QueueAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.room = SimpleNamespace(
            id="room-123",
            viewer_token="viewer-secret",
            control_token="control-secret",
        )
        self.auth = Authentication("server-secret")
        self.request_base = {
            "auth": self.auth,
            "state": SimpleNamespace(
                rooms=SimpleNamespace(
                    get=lambda room_id: (
                        self.room if room_id == "room-123" else None
                    )
                )
            ),
        }

    def request(self, token=None, room_id="room-123"):
        headers = {}
        if token is not None:
            headers["Authorization"] = token
        return SimpleNamespace(
            app=self.request_base,
            headers=headers,
            match_info={"room_id": room_id},
        )

    def test_control_token_can_access_queue_control_helper(self):
        self.assertIs(
            get_room_for_control(self.request("Bearer control-secret")),
            self.room,
        )

    def test_viewer_token_cannot_access_queue_control_helper(self):
        with self.assertRaises(web.HTTPUnauthorized):
            get_room_for_control(self.request("Bearer viewer-secret"))

    def test_missing_room_returns_not_found(self):
        with self.assertRaises(web.HTTPNotFound):
            get_room_for_control(self.request("Bearer control-secret", "missing"))


if __name__ == "__main__":
    unittest.main()
