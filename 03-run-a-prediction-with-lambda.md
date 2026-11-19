# 03 - Deploy a Prediction Function

**Goal:** Run the supplied Python handler in AWS and let it read exactly one
private S3 object. You will use the web editor and the console's test event
tool. There is no Function URL, public endpoint, or trigger in this step.

AWS Lambda runs your code on demand without a server for you to manage. Each
test sends a JSON **event** to the **handler** (the Python entry point) and
shows its return value. One run is called an **invocation**.

## 1. Create the Function and Deploy the Code

1. Use the top console search to open **Lambda** under **Services**. Choose
   **Create an Event Function** on the landing page, or **Event Functions →
   Create Event Function** if the list opens first. Do not choose Lambda Web.

   <details>
   <summary>Show the search results and Lambda landing page</summary>

   ![AWS service search results with Lambda under Services](assets/screenshots/03-find-lambda.jpg)

   ![Lambda Event section and the Create an Event Function link](assets/screenshots/03-lambda-landing.jpg)

   </details>

2. Choose **Author from scratch**. In **Function name**, enter a unique name
   such as `mleaws-predict-<suffix>`. In **Runtime**, choose **Python
   3.13**. Leave the other options as they are; do not add a public URL or
   event trigger. Choose **Create Event Function**.

   <details>
   <summary>Show runtime selection, the create form, and the welcome dialog</summary>

   ![Runtime picker with Python choices](assets/screenshots/03-runtime-picker.jpg)

   ![Create Event Function form with a Python runtime and the function name](assets/screenshots/03-create-function.jpg)

   ![Optional Getting started dialog after function creation](assets/screenshots/03-getting-started.jpg)

   </details>

3. If **Getting started** opens, choose **Dismiss**. In **Code → Code
   source**, open **lambda_function.py** in the web editor. Select all the
   starter code and replace it with [lambda_function.py](example/lambda_function.py).
   Choose **Deploy** and wait for **Lambda Deployed**. Leave the handler
   setting at `lambda_function.lambda_handler`. Do not click **Test** yet.

   ![Lambda browser editor showing the Python handler and Deploy controls](assets/screenshots/03-code-editor.jpg)

## 2. Set the Bucket Name

1. Choose **Configuration → Environment variables → Edit → Add environment
   variable**.

2. Set **Key** to `MODEL_BUCKET` and **Value** to the exact bucket name from
   lesson 02, without `s3://`, a path, quotation marks, or angle brackets.
   Choose **Save** and wait for the update. The bucket name is configuration,
   not a secret; never paste credentials into the example.

   <details>
   <summary>Show the Configuration tab and the environment variable form</summary>

   ![Lambda Configuration tab with Environment variables in the sidebar](assets/screenshots/03-configuration.jpg)

   ![Environment variables panel with the Edit button](assets/screenshots/03-environment-edit.jpg)

   ![Edit environment variables with MODEL_BUCKET and the Save button](assets/screenshots/03-environment-value.jpg)

   </details>

## 3. Give Lambda a Dedicated Role

AWS Identity and Access Management (IAM) controls who can do what. Your
function runs under an **execution role**, separate from your sign-in
identity. Its trust settings let Lambda use the role; its permission
policies say what the function can do. The new AWS experience may select a
built-in `PowerUserRole`. **Do not modify or use that role for the test.**
Create a role for this function instead.

1. In a separate tab for the same project, open **IAM → Roles → Create
   role**. In **Trusted entity type**, choose **AWS service**, then
   **Service or use case → Lambda**. Under **Use case**, keep **Lambda**
   selected and choose **Next**. This lets the Lambda service assume the role.

   <details>
   <summary>Show the Roles list and the Lambda trust selection</summary>

   ![IAM Roles list with Create role](assets/screenshots/03-iam-roles.jpg)

   ![IAM service dropdown with Lambda](assets/screenshots/03-iam-choose-service.jpg)

   ![Trusted entity step with AWS service and Lambda selected](assets/screenshots/03-iam-trust.jpg)

   </details>

2. In **Add permissions**, search for and check **AWSLambdaBasicExecutionRole**.
   This AWS-managed policy lets the function write to CloudWatch Logs, the
   service that collects its execution messages for troubleshooting.
   Choose **Next**. Enter the function name plus `-role` as **Role name**.
   Review the selected policy, then choose **Create role**.

   <details>
   <summary>Show the basic logging policy, role name, and creation result</summary>

   ![IAM results filtered to AWSLambdaBasicExecutionRole](assets/screenshots/03-iam-basic-logs.jpg)

   ![Review page with the dedicated execution role name](assets/screenshots/03-iam-role-review.jpg)

   ![IAM Roles list confirming the role was created](assets/screenshots/03-iam-role-created.jpg)

   </details>

3. Open your new role. Choose **Add permissions → Create inline policy →
   JSON**. Replace the editor contents with [read-model-policy.json](example/read-model-policy.json).
   In **Resource**, replace only `REPLACE_WITH_BUCKET_NAME` with your actual
   bucket name. Keep `/model.json` at the end: `s3:GetObject` allows reading
   that one object. Choose **Next**, name the policy `ReadPredictionModel`, then
   choose **Create policy**.

   <details>
   <summary>Show the inline-policy menu, JSON editor, and final review</summary>

   ![IAM Add permissions menu with Create inline policy](assets/screenshots/03-iam-inline-menu.jpg)

   ![JSON policy limiting s3:GetObject to model.json](assets/screenshots/03-iam-policy-json.jpg)

   ![Inline policy review with the ReadPredictionModel name](assets/screenshots/03-iam-policy-review.jpg)

   </details>

4. Return to Lambda. Choose **Configuration → General configuration →
   Edit**. Set **Memory** to **256 MB** and **Timeout** to **0 min 10 sec**
   so the first SDK call has time to finish. Under **Execution role**, choose
   your new role. Use **Refresh roles** or wait briefly if it is not listed.
   If your interface has role radio buttons, choose **Use an existing role**
   first. Choose **Save**.

   <details>
   <summary>Show the memory, timeout, and execution role settings</summary>

   ![Lambda basic settings with 256 MB, a 10-second timeout, and the dedicated execution role](assets/screenshots/03-lambda-resource-settings.jpg)

   </details>

5. Confirm **Configuration → Permissions → Execution role** shows your
   `-role`, not `PowerUserRole`. If creating or selecting the role is
   denied, stop and ask your coach. Do not try to fix this by adding
   administrator permissions or opening the bucket to the public.

## 4. Test a Successful Prediction and an Invalid Input

1. Choose the function's **Test** tab. Use **Create new event**,
   **Synchronous**, and **Private**. Enter `ValidPrediction` in **Event
   name** if prompted. Replace **Event JSON** with `{"x": 2}`. Choose
   **Test** (scroll back to the top of the event panel if needed).

   ![Lambda Test tab with the model input in the Event JSON editor](assets/screenshots/03-test-event.jpg)

2. Expand **Details** under **Executing function: succeeded**. Expect
   `"ok": true` and `"prediction": 5`. Keep the `request_id` for the
   CloudWatch walkthrough. Test `{"x": 7}` and expect `15`.

   ![Lambda succeeded banner with the Details disclosure below it](assets/screenshots/03-prediction-success.jpg)

3. Test `{"x": "two"}`. Expect `"ok": false` and a message explaining the
   valid range. Lambda can report that the invocation **succeeded**: the
   function ran and returned a validation error, rather than crashing.

| Test event | Expected response in Details |
| --- | --- |
| `{"x": 2}` | `"ok": true`, `"prediction": 5`, and a request ID |
| `{"x": 7}` | `"ok": true`, `"prediction": 15`, and a different request ID |
| `{"x": "two"}` | `"ok": false` and an error message describing the valid range |

| What you see | What to check |
| --- | --- |
| Placeholder Hello response | Paste the provided handler into the correct file and choose **Deploy**. |
| `KeyError: MODEL_BUCKET` | Confirm the environment variable is saved under the exact uppercase name. |
| S3 returns `AccessDenied` | Confirm the execution role and exact object ARN. Wait briefly after a role or policy change. S3 can also return 403 for a missing key when the role cannot list the bucket. |
| A timeout on the first call | Verify that the 256 MB and 10-second settings were saved and that no custom VPC is attached. Retry once. |

**Checkpoint:** You deployed and invoked code on AWS without exposing a
public URL. Continue with [04 - Read the Logs](04-read-logs-in-cloudwatch.md).
