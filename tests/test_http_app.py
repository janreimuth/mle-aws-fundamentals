import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

EXAMPLE = Path(__file__).resolve().parents[1] / "example"
with patch.object(sys, "path", [str(EXAMPLE), *sys.path]):
    import http_app
    import lambda_function


class WebPredictionTests(unittest.TestCase):
    def invoke(self, event):
        return http_app.lambda_handler(
            event, SimpleNamespace(aws_request_id="web-test")
        )

    def test_page_submits_to_same_origin(self):
        page = self.invoke({"routeKey": "GET /"})
        self.assertEqual(page["statusCode"], 200)
        self.assertIn("text/html", page["headers"]["content-type"])
        self.assertIn("fetch('/predict'", page["body"])

    def test_predictions_and_original_console_event(self):
        with patch.object(
            lambda_function,
            "read_model",
            return_value=json.loads((EXAMPLE / "model.json").read_text()),
        ):
            for x, expected in [(2, 5), (7, 15)]:
                result = self.invoke(
                    {"routeKey": "POST /predict", "body": json.dumps({"x": x})}
                )
                self.assertEqual(result["statusCode"], 200)
                self.assertEqual(json.loads(result["body"]), self.invoke({"x": x}))
                self.assertEqual(json.loads(result["body"])["prediction"], expected)

    def test_invalid_requests(self):
        for body in ("not JSON", ""):
            with self.subTest(body=body):
                self.assertEqual(
                    self.invoke({"routeKey": "POST /predict", "body": body})[
                        "statusCode"
                    ],
                    400,
                )
        for body in ("null", '{"x": true}'):
            with self.subTest(body=body), self.assertLogs(level="WARNING") as logs:
                result = self.invoke({"routeKey": "POST /predict", "body": body})
                self.assertEqual(result["statusCode"], 400)
                self.assertIn("validation_error request_id=web-test", logs.output[0])
        self.assertEqual(self.invoke({"routeKey": "GET /predict"})["statusCode"], 404)
