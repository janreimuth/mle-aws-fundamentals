import json
import unittest
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from example import lambda_function

MODEL = Path(__file__).resolve().parents[1] / "example" / "model.json"
CONTEXT = SimpleNamespace(aws_request_id="test-invocation")


class PredictionTests(unittest.TestCase):
    def test_predictions_use_supplied_model(self):
        with patch.object(
            lambda_function, "read_model", return_value=json.loads(MODEL.read_text())
        ):
            for x, expected in [(2, 5), (7, 15), (-3, -5)]:
                with self.subTest(x=x):
                    result = lambda_function.lambda_handler({"x": x}, CONTEXT)
                    self.assertEqual(
                        result,
                        {
                            "ok": True,
                            "prediction": expected,
                            "request_id": "test-invocation",
                        },
                    )

    def test_invalid_input_does_not_request_model(self):
        with patch.object(lambda_function, "read_model") as read_model:
            with self.assertLogs(lambda_function.logger, level="WARNING"):
                for event in (
                    {},
                    None,
                    {"x": "two"},
                    {"x": True},
                    {"x": float("nan")},
                    {"x": 1e7},
                ):
                    with self.subTest(event=event):
                        self.assertFalse(
                            lambda_function.lambda_handler(event, CONTEXT)["ok"]
                        )
            read_model.assert_not_called()

    def test_loads_the_configured_s3_object(self):
        s3 = Mock()
        s3.get_object.return_value = {"Body": BytesIO(b'{"slope": 2, "intercept": 3}')}
        boto3 = SimpleNamespace(client=Mock(return_value=s3))
        with (
            patch.dict("sys.modules", {"boto3": boto3}),
            patch.dict("os.environ", {"MODEL_BUCKET": "example-bucket"}),
        ):
            result = lambda_function.lambda_handler({"x": 2}, CONTEXT)

        boto3.client.assert_called_once_with("s3")
        s3.get_object.assert_called_once_with(Bucket="example-bucket", Key="model.json")
        self.assertEqual(result["prediction"], 7)
