"""Smoke tests for startup and the environment-driven HTTP configuration."""

import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import create_app


class AppTests(unittest.TestCase):
    def setUp(self):
        with patch.dict(os.environ, {
            "ALLOWED_HOSTS": '["localhost", "backend"]',
            "ALLOWED_ORIGINS": '["http://localhost:5173"]',
        }):
            self.client = TestClient(create_app(), base_url="http://localhost")
        self.addCleanup(self.client.close)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_compose_hostname(self):
        self.assertEqual(self.client.get("http://backend/health").status_code, 200)

    def test_untrusted_hostname(self):
        self.assertEqual(self.client.get("http://untrusted.invalid/health").status_code, 400)

    def test_frontend_cors(self):
        response = self.client.options("/health", headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "http://localhost:5173")


if __name__ == "__main__":
    unittest.main()
