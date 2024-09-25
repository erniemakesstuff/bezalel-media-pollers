from types import SimpleNamespace
from sqs_polling import sqs_polling
import os
import json
import logging
import sys

import boto3

from botocore.exceptions import ClientError

import queue_wrapper
from callbacks import CallbackHandler
import clients.gemini as gemini

logger = logging.getLogger(__name__)
session = boto3.Session(
    region_name= os.environ['AWS_REGION'],
    aws_access_key_id= os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key= os.environ['AWS_SECRET_ACCESS_KEY'],
)
sqs = session.client("sqs")
aws_profile = {
    "region_name": os.environ['AWS_REGION'],
    "aws_access_key_id": os.environ['AWS_ACCESS_KEY_ID'],
    "aws_secret_access_key": os.environ['AWS_SECRET_ACCESS_KEY'],
}
# TODO: Assign these variables as env args to startup script
targetGenerator = "TextMedia" #os.environ['TARGET_GENERATOR']
media_text_queue = "https://sqs.us-west-2.amazonaws.com/971422718801/media-text-queue"
visibility_timeout_seconds = 20 # TODO: Update this longer!
poll_delay_seconds = 5 # Polling interval
max_workers = 1


callback_handler = CallbackHandler(targetGenerator=targetGenerator)
logger.info("Starting polling...")
while True:
    queue_wrapper.poll(media_text_queue, callback_handler.handle_message,
                    visibility_timeout_seconds,
                    poll_delay_seconds)



