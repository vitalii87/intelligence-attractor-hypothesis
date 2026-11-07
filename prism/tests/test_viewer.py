import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest

from prism.viewer import make_server
from test_run_view import fixture


class ViewerHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        fixture(cls.root)
        cls.server = make_server([cls.root], port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        cls.tmp.cleanup()

    def get(self, path, headers=None, method="GET"):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            connection.request(method, path, headers=headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_assets_api_and_content_policy(self):
        for path in ("/", "/app.js", "/style.css", "/api/runs", "/api/run?id=0"):
            status, headers, body = self.get(path)
            self.assertEqual(status, 200)
            self.assertTrue(body)
            self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
            self.assertEqual(headers["Cache-Control"], "no-store")
        result = json.loads(self.get("/api/run?id=0")[2])
        self.assertEqual(result["attempts"][0]["artifact_integrity"], "verified")

    def test_rebinding_cross_origin_and_arbitrary_file_access_refused(self):
        self.assertEqual(self.get("/api/runs", {"Host": "evil.test"})[0], 403)
        self.assertEqual(self.get("/api/runs", {"Origin": "https://evil.test"})[0], 403)
        self.assertEqual(self.get("/api/run?id=../../secret")[0], 404)
        self.assertEqual(self.get("/config.toml")[0], 404)
        self.assertEqual(self.get("/../iteration-state.json")[0], 404)
        self.assertEqual(self.get("/api/run?id=0&id=1")[0], 404)
        self.assertEqual(self.get("/api/run?id=0", method="POST")[0], 501)

    def test_invalid_run_is_a_readable_error_not_traceback(self):
        path = self.root / "iteration-state.json"
        original = path.read_bytes()
        try:
            path.write_text("broken")
            status, _, body = self.get("/api/run?id=0")
            self.assertEqual(status, 422)
            self.assertIn("error", json.loads(body))
            self.assertNotIn("Traceback", body.decode())
        finally:
            path.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
