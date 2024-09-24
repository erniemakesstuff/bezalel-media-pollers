import json
from types import SimpleNamespace
import boto3
import os
import logging
session = boto3.Session(
    region_name= os.environ['AWS_REGION'],
    aws_access_key_id= os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key= os.environ['AWS_SECRET_ACCESS_KEY'],
)
logger = logging.getLogger(__name__)

# Create SQS client
sqs = session.client('sqs')


def poll(queue_url: str, callbackFunc, visibilityTimeout, waitTimeSeconds):
    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=visibilityTimeout,
        WaitTimeSeconds=waitTimeSeconds
    )
    if not "Messages" in response:
        print("EMPTY Q")
        return
    message = response['Messages'][0]
    receipt_handle = message['ReceiptHandle']
    sqsBodyStr = message["Body"]
    messageDetails = json.loads(sqsBodyStr)
    mediaEvent =  json.loads(messageDetails["Message"], object_hook=lambda d: SimpleNamespace(**d))
   

    success = callbackFunc(mediaEvent)
    # Delete received message from queue
    if success:
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
    else:
        logger.error("failed to process message: " + mediaEvent.EventID)