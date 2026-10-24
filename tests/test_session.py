import unittest

from src.utils.comix_session import publish_comix_credentials
from src.utils.session import SessionManager


class FakeSession:
    def __init__(self):
        self.headers = {}
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return object()


class SessionManagerTests(unittest.TestCase):
    def test_comix_requests_receive_referer_and_cookies(self):
        manager = SessionManager()
        session = FakeSession()
        manager._local.session = session
        publish_comix_credentials("browser-agent", [
            type("Cookie", (), {"name": "cf_clearance", "value": "clear", "domain": ".comix.to"})()
        ])
        manager.get("https://comix.to/api/v1/manga")

        headers = session.calls[0][1]["headers"]
        self.assertEqual(headers["Referer"], "https://comix.to/")
        self.assertEqual(headers["Cookie"], "cf_clearance=clear")

    def test_image_cdn_requests_do_not_receive_comix_referer(self):
        manager = SessionManager()
        session = FakeSession()
        manager._local.session = session
        manager.get("https://8pl.example.site/image")

        self.assertNotIn("headers", session.calls[0][1])
