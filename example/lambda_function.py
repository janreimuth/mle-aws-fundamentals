import json
import logging
import math
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def read_model():
    import boto3

    response = boto3.client("s3").get_object(
        Bucket=os.environ["MODEL_BUCKET"], Key="model.json"
    )
    with response["Body"] as body:
        return json.load(body)


def lambda_handler(event, context):
    x = event.get("x") if isinstance(event, dict) else None
    request_id = context.aws_request_id

    if (
        isinstance(x, bool)
        or not isinstance(x, (int, float))
        or not -1_000_000 <= x <= 1_000_000
    ):
        logger.warning("validation_error request_id=%s", request_id)
        return {"ok": False, "error": "x must be a number between -1000000 and 1000000"}

    model = read_model()
    prediction = model["slope"] * x + model["intercept"]
    if not math.isfinite(prediction):
        raise ValueError("The model produced a non-finite prediction")
    logger.info("prediction request_id=%s result=%s", request_id, prediction)
    return {"ok": True, "prediction": prediction, "request_id": request_id}
