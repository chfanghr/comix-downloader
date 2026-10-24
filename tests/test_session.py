import unittest
from unittest.mock import patch

import requests

from src.utils.comix_session import publish_comix_credentials
from src.utils.session import SessionManager


class SessionManagerTests(unittest.TestCase):
    def test_comix_requests_receive_referer_and_cookies(self):
        manager = SessionManager()
        publish_comix_credentials("browser-agent", [
            type("Cookie", (), {"name": "cf_clearance", "value": "clear", "domain": ".comix.to"})()
        ])
        response = requests.Response()
        response.status_code = 200

        with patch.object(manager.session, "get", return_value=response) as get:
            manager.get("https://comix.to/api/v1/manga")

        headers = get.call_args.kwargs["headers"]
        self.assertEqual(headers["Referer"], "https://comix.to/")
        self.assertEqual(headers["Cookie"], "cf_clearance=clear")

    def test_image_cdn_requests_do_not_receive_comix_referer(self):
        manager = SessionManager()
        response = requests.Response()
        response.status_code = 200

        with patch.object(manager.session, "get", return_value=response) as get:
            manager.get("https://8pl.example.site/image")

        self.assertNotIn("headers", get.call_args.kwargs)
