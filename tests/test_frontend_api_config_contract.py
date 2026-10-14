"""Source contract checks for the browser API endpoint configuration."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class FrontendApiConfigContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")

    def test_first_visit_and_invalid_or_empty_saved_values_use_production_default(self):
        self.assertIn(
            'const DEFAULT_API_BASE = "https://45g0v7hvbh.execute-api.ap-south-1.amazonaws.com/prod";',
            self.app,
        )
        api_base = self.app.split("function apiBase()", 1)[1].split(
            "function isValidApiBase", 1
        )[0]
        self.assertIn("localStorage.getItem(API_STORAGE_KEY)", api_base)
        self.assertIn("saved && isValidApiBase(saved)", api_base)
        self.assertIn(": DEFAULT_API_BASE", api_base)
        self.assertIn("catch (_) {\n    return DEFAULT_API_BASE;", api_base)

    def test_valid_local_development_endpoint_remains_supported(self):
        validator = self.app.split("function isValidApiBase", 1)[1].split(
            "async function setApiBase", 1
        )[0]
        self.assertIn('url.hostname === "localhost"', validator)
        self.assertIn('url.hostname === "127.0.0.1"', validator)
        self.assertIn('url.port === "3000"', validator)
        self.assertIn("url.protocol === \"http:\"", validator)

    def test_base_is_normalized_and_all_api_routes_use_the_shared_helper(self):
        api_base = self.app.split("function apiBase()", 1)[1].split(
            "function isValidApiBase", 1
        )[0]
        self.assertIn(".replace(/\\/+$/, \"\")", api_base)
        self.assertIn("fetch(base + path, options)", self.app)
        for route in (
            'api("/uploads"',
            'api("/history"',
            'api(`/images/${encodeURIComponent(imageId)}`',
            'method: "DELETE"',
        ):
            with self.subTest(route=route):
                self.assertIn(route, self.app)
        self.assertNotRegex(self.app, r"fetch\(\s*['\"]https://45g0v7hvbh")

    def test_settings_still_accept_and_save_endpoint_overrides(self):
        settings = self.app.split("async function setApiBase()", 1)[1].split(
            "/* Make API requests */", 1
        )[0]
        self.assertIn("window.prompt(", settings)
        self.assertIn("isValidApiBase(cleaned)", settings)
        self.assertIn("localStorage.setItem(API_STORAGE_KEY, cleaned)", settings)
        self.assertIn("await refreshAll()", settings)
        self.assertIn("reset to the production default", settings)


if __name__ == "__main__":
    unittest.main()
