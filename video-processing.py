import json
import boto3   # pyright: ignore[reportMissingImports]
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    print("Received event:" + json.dumps(event))
    
    for record in event['Records']:
        # SQS message body contains SNS message as JSON string
        sns_message_str = record['body']
        sns_message = json.loads(sns_message_str)

        # The actual S3 event message is inside the SNS 'Message' field as JSON string
        s3_event_str = sns_message['Message']
        s3_event = json.loads(s3_event_str)

        for rec in s3_event['Records']:
            source_bucket = rec['s3']['bucket']['name']
            source_key = rec['s3']['object']['key']

            # Decode URL encoded S3 key if needed
            source_key = source_key.replace('+', ' ')

            print(f"Source bucket: {source_bucket}, key: {source_key}")

            # Download the file to /tmp
            download_path = f"/tmp/{os.path.basename(source_key)}"
            s3.download_file(source_bucket, source_key, download_path)
            print(f"File downloaded to {download_path}")

            # For demo: just rename file as processed-<original_name>
            processed_filename = f"processed-{os.path.basename(source_key)}"

            # Upload the file to destination bucket
            dest_bucket = 'dest-sns-v6'
            dest_key = processed_filename
            s3.upload_file(download_path, dest_bucket, dest_key)
            print(f"Uploaded processed file to s3://{dest_bucket}/{dest_key}")

    return {
        'statusCode': 200,
        'body': json.dumps('Processing Complete')
    }

