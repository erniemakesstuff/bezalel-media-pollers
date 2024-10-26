import traceback
from types import SimpleNamespace
import os
import json
import logging
import sys

import boto3

from botocore.exceptions import ClientError

import queue_wrapper
from callbacks.callback_factory import CallbackFactory
from callbacks.text_callback import TextCallbackHandler
from callbacks.render_callback import RenderCallbackHandler
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
targetGenerator = os.environ['TARGET_GENERATOR']
media_text_queue = "https://sqs.us-west-2.amazonaws.com/971422718801/media-text-queue"
media_render_queue = "https://sqs.us-west-2.amazonaws.com/971422718801/media-render-queue"
visibility_timeout_seconds = 60 # TODO: Update this longer!
poll_delay_seconds = 5 # Polling interval
max_workers = 1 # TODO: probably not needed anymore: generators should use max container resources on single-op.
def start_poll():
    # Local testing convenience
    if targetGenerator == 'local':
        while True:
            try:
                queue_wrapper.poll(media_text_queue, TextCallbackHandler(targetGenerator=targetGenerator).handle_message,
                                visibility_timeout_seconds,
                                poll_delay_seconds)
            except Exception:
                print("exception in poller: " + traceback.format_exc())
            try:
                queue_wrapper.poll(media_render_queue, RenderCallbackHandler(targetGenerator=targetGenerator).handle_message,
                                visibility_timeout_seconds,
                                poll_delay_seconds)
            except Exception:
                print("exception in poller: " + traceback.format_exc())


    callback_handler = CallbackFactory().getCallbackInstance(targetGenerator=targetGenerator)
    work_queue = ""
    if targetGenerator == 'Text':
        work_queue = media_text_queue
    elif targetGenerator == 'Render':
        work_queue = media_render_queue
    else:
        raise Exception("invalid targetGenerator: " + targetGenerator)
    logger.info("Starting polling...")
    # TODO: only one poller should be active! Remove duplicate pollers when
    # containerizing. Added only for local-dev convenience.
    while True:
        try:
            queue_wrapper.poll(work_queue, callback_handler.handle_message,
                            visibility_timeout_seconds,
                            poll_delay_seconds)
        except Exception:
            print("exception in poller: " + traceback.format_exc())