from types import SimpleNamespace
import os
import json
import logging
import sys
import requests
import boto3
import time

from botocore.exceptions import ClientError
import s3_wrapper
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
        logger.info("MediaType: " + mediaEvent.MediaType)
        if s3_wrapper.media_exists(mediaEvent.ContentLookupKey):
            return True
        return self.handle_image_generation(mediaEvent)

    def handle_image_generation(self, mediaEvent) -> bool:
        logger.info("SystemPromptInstruction: " + mediaEvent.SystemPromptInstruction)
        logger.info("PromptInstruction: " + mediaEvent.PromptInstruction)
        url = os.environ["SIMPLE_IMAGE_GENERATOR_ENDPOINT"]
        requestObj = {
            "promptInstruction": mediaEvent.PromptInstruction,
            "contentLookupKey": mediaEvent.ContentLookupKey,
        }
        result = requests.post(url, requestObj, verify=False, timeout=180)
        if not result.ok:
            return False
        
        # TODO store s3 by callback id if integrating with third-party apis.
        fileName = os.environ["SHARED_MEDIA_VOLUME_PATH"] + mediaEvent.ContentLookupKey + ".png"

        # wait for the file to be ready
        max_wait_iterations = 5 # 5min
        wait_iteration = 1
        while not os.path.exists(fileName) and wait_iteration <= max_wait_iterations:
            logger.info("Waiting for file to be created: " + fileName)
            time.sleep(60)
            wait_iteration += 1

        if os.path.exists(fileName):
            logger.info("File was not generated; timeout: " + fileName)
            return False
        
        success = s3_wrapper.upload_file(fileName, mediaEvent.ContentLookupKey)
        os.remove(fileName)
        logger.info("Generated conetent: " + fileName)
        return success