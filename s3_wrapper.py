import json
from types import SimpleNamespace
import boto3
import os
import logging
from botocore.exceptions import ClientError
session = boto3.Session(
    region_name= os.environ['AWS_REGION'],
    aws_access_key_id= os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key= os.environ['AWS_SECRET_ACCESS_KEY'],
)
logger = logging.getLogger(__name__)
s3_client = session.client('s3')
# TODO make this env set.
bucket = "truevine-media-storage"

#S3 Docs: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
def upload_file(file_path_name, callbackId) -> bool:
    """Upload a file to an S3 bucket

    :param file_path_name: File to upload
    :param callbackId: S3 object name. Should be MediaEvent callback ID.
    :return: True if file was uploaded, else False
    """
    
    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_path_name, bucket, callbackId)
    except ClientError as e:
        logging.error(e)
        return False
    return True