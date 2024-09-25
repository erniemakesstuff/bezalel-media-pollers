from types import SimpleNamespace
from sqs_polling import sqs_polling
import os
import json
import logging
import sys

import boto3

from botocore.exceptions import ClientError

import queue_wrapper
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
targetCallback = "TODO"
media_text_queue = "https://sqs.us-west-2.amazonaws.com/971422718801/media-text-queue"
visibility_timeout_seconds = 20 # TODO: Update this longer!
poll_delay_seconds = 1 # Polling interval
max_workers = 1
# TODO: Ensure to call some standard "warm" or "init" function as a blocking call prior to polling.
# LLMs take awhile to load.
geminiInst = gemini.GeminiClient()
geminiInst.call_model()
def my_callback(mediaEvent) -> bool:
    logger.info("BodyMessage: " + mediaEvent.MediaType)
    return True


# TODO, wrap this in a while-loop after grace period
logger.info("Starting polling...")
queue_wrapper.poll(media_text_queue, my_callback,
                   visibility_timeout_seconds,
                   poll_delay_seconds)