import boto3
import botocore
import logging
import os

def upload(image_data, object_name):
    s3 = boto3.client("s3")

    try:
        response = s3.put_object(Body=image_data, Bucket=os.getenv("S3_BUCKET"), Key=object_name)
    except botocore.exceptions.ClientError as e:
        logging.error(e)
        return False

    return True
