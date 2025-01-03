import time
import traceback
from types import SimpleNamespace
import os
import json
import logging
import sys

import boto3

from botocore.exceptions import ClientError
import multiprocessing
import queue_wrapper
from callbacks.callback_factory import CallbackFactory
from callbacks.text_callback import TextCallbackHandler
from callbacks.render_callback import RenderCallbackHandler
from callbacks.image_callback import ImageCallbackHandler
from callbacks.vocal_callback import VocalCallbackHandler
from callbacks.context_callback import ContextCallbackHandler
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
media_image_queue = "https://sqs.us-west-2.amazonaws.com/971422718801/media-image-queue"
media_vocal_queue = "https://sqs.us-west-2.amazonaws.com/971422718801/media-vocal-queue"
media_context_queue = "https://sqs.us-west-2.amazonaws.com/971422718801/media-context-queue"

class Consumer:
    def __new__(cls):
        logger.info("created new consumer instance: " + str(os.getpid()))
        if not hasattr(cls, 'instance'):
            cls.instance = super(Consumer, cls).__new__(cls)
        return cls.instance
    
    def create_poll_workers(self, max_workers = 1, poll_delay_seconds = 5, visibility_timeout_seconds = 60):
        i = 0
        workers = []
        while i < max_workers:
            p = multiprocessing.Process(target=self.start_poll, args=(poll_delay_seconds, visibility_timeout_seconds))
            p.start()
            workers.append(p)
            i += 1
            time.sleep(3) # stagger workers so they don't poll the same data.

        for w in workers:
            w.join()

    def start_poll(self, poll_delay_seconds = 5, visibility_timeout_seconds = 60):
        # Local testing convenience
        if targetGenerator == 'local':
            while True:
                try:
                    queue_wrapper.poll(media_text_queue, TextCallbackHandler().handle_message,
                                    visibility_timeout_seconds,
                                    poll_delay_seconds)
                except Exception:
                    logger.info("exception in poller: " + traceback.format_exc())
                try:
                    queue_wrapper.poll(media_render_queue, RenderCallbackHandler().handle_message,
                                    visibility_timeout_seconds,
                                    poll_delay_seconds)
                except Exception:
                    logger.info("exception in poller: " + traceback.format_exc())
                try:
                    queue_wrapper.poll(media_image_queue, ImageCallbackHandler().handle_message,
                                    visibility_timeout_seconds,
                                    poll_delay_seconds)
                except Exception:
                    logger.info("exception in poller: " + traceback.format_exc())
                try:
                    queue_wrapper.poll(media_vocal_queue, VocalCallbackHandler().handle_message,
                                    visibility_timeout_seconds,
                                    poll_delay_seconds)
                except Exception:
                    logger.info("exception in poller: " + traceback.format_exc())
                try:
                    queue_wrapper.poll(media_context_queue, ContextCallbackHandler().handle_message,
                                    visibility_timeout_seconds,
                                    poll_delay_seconds)
                except Exception:
                    logger.info("exception in poller: " + traceback.format_exc())


        callback_handler = CallbackFactory().getCallbackInstance(targetGenerator=targetGenerator)
        work_queue = ""
        if targetGenerator == 'Text':
            work_queue = media_text_queue
        elif targetGenerator == 'Render':
            work_queue = media_render_queue
        elif targetGenerator == 'Image':
            work_queue = media_image_queue
        elif targetGenerator == 'Vocal':
            work_queue = media_vocal_queue
        elif targetGenerator == 'Context':
            work_queue = media_context_queue
        else:
            raise Exception("invalid targetGenerator: " + targetGenerator)
        logger.info("Starting polling...")
        while True:
            try:
                queue_wrapper.poll(work_queue, callback_handler.handle_message,
                                visibility_timeout_seconds,
                                poll_delay_seconds)
            except Exception:
                logger.info("exception in poller: " + traceback.format_exc())