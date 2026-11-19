"""API Gateway HTTP API, payload format 2.0. Deploy beside lambda_function.py."""

import json

from lambda_function import lambda_handler as predict

PAGE = """<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Model prediction</title>
<main><h1>Try the S3 model</h1><form>
<label>Input x <input name="x" type="number" step="any" min="-1000000" max="1000000" required value="2"></label>
<button>Predict</button></form><p role="status"></p></main>
<script>
document.querySelector('form').onsubmit = async event => {
  event.preventDefault();
  const status = document.querySelector('[role=status]');
  status.textContent = 'Predicting...';
  try {
    const response = await fetch('/predict', {method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({x: event.target.elements.x.valueAsNumber})});
    const data = await response.json();
    status.textContent = response.ok ? 'Prediction: ' + data.prediction +
      ' | Request ID: ' + data.request_id : data.error || 'Prediction failed';
  } catch { status.textContent = 'Could not reach the prediction API.'; }
};
</script></html>"""


def lambda_handler(event, context):
    route = event.get("routeKey")
    if route is None:
        return predict(event, context)  # Preserve the earlier console test.
    if route == "GET /":
        return {
            "statusCode": 200,
            "headers": {"content-type": "text/html; charset=utf-8"},
            "body": PAGE,
        }
    if route == "POST /predict":
        try:
            payload = json.loads(event.get("body") or "")
        except (ValueError, TypeError):
            result = {"ok": False, "error": "Send a JSON body containing x."}
        else:
            result = predict(payload, context)
        code = 200 if result["ok"] else 400
    else:
        code, result = 404, {"error": "Unknown route"}
    return {
        "statusCode": code,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(result),
    }
