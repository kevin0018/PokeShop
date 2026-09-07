import os
import unittest
from unittest.mock import patch

from src.database import database_url


class DatabaseConfigTests(unittest.TestCase):
    def test_password_special_characters_roundtrip(self):
        with patch.dict(
            os.environ, {"POSTGRES_PASSWORD": "a@b:/?#% c"}, clear=True
        ), patch("src.database.load_dotenv"):
            url = database_url()
            self.assertEqual(url.password, "a@b:/?#% c")
            self.assertNotIn("a@b", str(url))

    def test_missing_secret_has_actionable_error(self):
        with patch.dict(os.environ, {}, clear=True), patch("src.database.load_dotenv"):
            with self.assertRaisesRegex(RuntimeError, "POSTGRES_PASSWORD"):
                database_url()
