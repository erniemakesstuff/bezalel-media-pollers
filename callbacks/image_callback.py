from types import SimpleNamespace
import os
import json
import logging
import sys
from urllib.parse import urlencode
import requests
import boto3
import time

from botocore.exceptions import ClientError
import s3_wrapper
from callbacks.common_callback import request_and_wait
logger = logging.getLogger(__name__)
# Used for initial scripting.
class ImageCallbackHandler(object):
    geminiInst = None
    targetGenerator = None
    def __new__(cls, targetGenerator):
        if not hasattr(cls, 'instance'):
             cls.instance = super(ImageCallbackHandler, cls).__new__(cls)
        cls.targetGenerator = targetGenerator
        return cls.instance
    # Common interface.
    def handle_message(self, mediaEvent) -> bool:
        if s3_wrapper.media_exists(mediaEvent.ContentLookupKey):
            return True
        return self.handle_image_generation(mediaEvent)

    def handle_image_generation(self, mediaEvent) -> bool:
        url = os.environ["SIMPLE_IMAGE_GENERATOR_ENDPOINT"]
        request_obj = {
            "promptInstruction": mediaEvent.PromptInstruction,
            "contentLookupKey": mediaEvent.ContentLookupKey,
        }
        return request_and_wait(url, 5, request_obj, mediaEvent.ContentLookupKey)