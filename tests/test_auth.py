import unittest
from types import SimpleNamespace

from aiohttp import web

from _core._core_func._auth._auth import Authentication


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.auth = Authentication("server-secret")
        self.room = SimpleNamespace(
            viewer_token="viewer-secret",
            control_token="control-secret",
        )

    @staticmethod
    def request(token=None):
        headers = {}
        if token is not None:
            headers["Authorization"] = token
        return SimpleNamespace(headers=headers)

    def assert_unauthorized(self, callback, request, *args):
        with self.assertRaises(web.HTTPUnauthorized):
            callback(request, *args)

    def test_global_bearer_key_is_accepted(self):
        self.assertTrue(
            self.auth._verify(self.request("Bearer server-secret"))
        )

    def test_global_auth_rejects_missing_or_wrong_key(self):
        self.assert_unauthorized(self.auth._verify, self.request())
        self.assert_unauthorized(
            self.auth._verify,
            self.request("Bearer wrong-secret"),
        )

    def test_viewer_token_can_read_room(self):
        self.assertTrue(
            self.auth._verify_room_access(
                self.request("Bearer viewer-secret"),
                self.room,
            )
        )

    def test_control_token_can_read_room(self):
        self.assertTrue(
            self.auth._verify_room_access(
                self.request("Bearer control-secret"),
                self.room,
            )
        )

    def test_global_key_can_read_room(self):
        self.assertTrue(
            self.auth._verify_room_access(
                self.request("Bearer server-secret"),
                self.room,
            )
        )

    def test_viewer_token_cannot_control_room(self):
        self.assert_unauthorized(
            self.auth._verify_room_control,
            self.request("Bearer viewer-secret"),
            self.room,
        )

    def test_control_token_can_control_room(self):
        self.assertTrue(
            self.auth._verify_room_control(
                self.request("Bearer control-secret"),
                self.room,
            )
        )

    def test_global_key_can_control_room(self):
        self.assertTrue(
            self.auth._verify_room_control(
                self.request("Bearer server-secret"),
                self.room,
            )
        )

    def test_room_access_rejects_missing_and_wrong_credentials(self):
        self.assert_unauthorized(
            self.auth._verify_room_access,
            self.request(),
            self.room,
        )
        self.assert_unauthorized(
            self.auth._verify_room_access,
            self.request("Bearer wrong-secret"),
            self.room,
        )

    def test_control_access_rejects_missing_and_wrong_credentials(self):
        self.assert_unauthorized(
            self.auth._verify_room_control,
            self.request(),
            self.room,
        )
        self.assert_unauthorized(
            self.auth._verify_room_control,
            self.request("Bearer wrong-secret"),
            self.room,
        )

    def test_empty_configured_key_is_rejected(self):
        for value in ("", "   "):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Authentication(value)

    def test_missing_configured_key_generates_nonempty_secret(self):
        auth = Authentication()
        self.assertTrue(auth.auth_key)
        self.assertNotEqual(auth.auth_key, self.auth.auth_key)


if __name__ == "__main__":
    unittest.main()
