cat > README.md <<'EOF'
# AWS S3-SNS-SQS-Lambda Video Processing Pipeline

This repository demonstrates a **serverless video processing workflow** using AWS services including S3, SNS, SQS, and Lambda. The pipeline processes uploaded MP4 files from a raw S3 bucket, runs a lightweight transformation (using an FFmpeg layer in Lambda), and stores the processed file in the destination S3 bucket.

---

## Architecture
[Architecture](architecture.png)

**High-level flow:**
1. Upload video → `raw-bucket-v6`
2. S3 event notification sends message to **SNS topic** `video-uploaded`
3. **SNS** publishes to **SQS** queue `video-processing-queue`
4. **Lambda** (`video-processing`) is triggered by SQS, downloads file from S3, processes it via FFmpeg layer, then uploads processed file to `dest-sns-v6`
5. CloudWatch captures logs and execution metrics

---

## Files in this repo
- `lambda/video-processing.py` — Lambda function code
- `lambda/ffmpeg-layer-info.txt` — info / ARN placeholder for FFmpeg lambda layer
- `architecture.png` — visual architecture diagram
- `screenshots/` — place your screenshots here

---

## Prerequisites
- AWS account with permissions to create S3, SNS, SQS, Lambda, IAM roles and CloudWatch.
- AWS CLI configured, or use the AWS Console.
- A prebuilt FFmpeg Lambda Layer (you can use a community layer or build your own).
- Python 3.9 runtime for Lambda (matching this code).

---

## Deployment / Setup Steps (detailed)

1. **Create S3 buckets**
   - `raw-bucket-v6` — where you upload input videos
   - `dest-sns-v6` — where processed videos will be stored

2. **Create SNS topic**
   - Name: `video-uploaded`

3. **Create SQS queue**
   - Name: `video-processing-queue`
   - Configure queue access policy so SNS can send messages to it (subscribe the queue to the SNS topic).

4. **Subscribe SQS to SNS**
   - SNS Topic: `video-uploaded`
   - Endpoint: `video-processing-queue` (SQS protocol)
   - Test: publish a test message to SNS and verify it appears in the SQS queue.

5. **Configure S3 Event Notification**
   - On `raw-bucket-v6` add an **Event Notification** for **All object create events** that targets SNS topic `video-uploaded`.
   - Test by uploading a small MP4; verify S3 fired a notification (message appears in SQS).

6. **Create IAM Role for Lambda**
   - Role name: e.g., `Lambda-role-for-SNS`
   - Minimum permissions required:
     - `AmazonS3FullAccess` (or a scoped policy allowing GetObject/PutObject for the two buckets)
     - `AmazonSQSFullAccess` (or scoped SQS Receive/ChangeMessageVisibility/DeleteMessage)
     - `AWSLambdaBasicExecutionRole` (CloudWatch logs)
   - (For production, scope policies to least privilege — see Troubleshooting & Security notes.)

7. **Create Lambda Function**
   - Name: `video-processing`
   - Runtime: Python 3.9
   - Handler: `video-processing.lambda_handler` (if filename is `video-processing.py`)
   - Attach IAM role created in step 6.
   - Add a Layer: FFmpeg Lambda Layer (ARN in `lambda/ffmpeg-layer-info.txt`).

8. **Add SQS trigger**
   - Add `video-processing-queue` as an event source mapping with Batch size: `1`.

9. **Deploy code**
   - Upload `lambda/video-processing.py` using the console, AWS CLI, SAM, or CDK.
   - Ensure the Lambda timeout is sufficient for processing (start with 1–2 minutes for testing).
   - Ensure `/tmp` has enough space — for large videos you might need a different architecture (ECS/Batch/Step Functions).

10. **Test the flow**
    - Upload an MP4 to `raw-bucket-v6`.
    - Watch CloudWatch logs for Lambda invocation, SQS visibility, and successful upload to `dest-sns-v6`.

---

## Troubleshooting
- **No message in SQS:** verify SNS subscription status and S3 event configuration. Check SNS delivery retry and permissions.
- **AccessDenied on S3:** confirm Lambda role has correct S3 permissions.
- **Lambda times out:** increase timeout, or process smaller files and test step-by-step.
- **/tmp space errors:** Lambda has limited ephemeral storage (512 MB by default). For larger files use larger tmp or an alternative architecture.

---

## Security & Hardening
- Replace `AmazonS3FullAccess` and `AmazonSQSFullAccess` with least-privilege policies scoped to resources.
- Use KMS for encryption if required.
- Enable S3 object-level logging / event history to detect rogue uploads.

---

## Author
Gatla Sridhar Apoorva
AWS Enthusiast
EOF
