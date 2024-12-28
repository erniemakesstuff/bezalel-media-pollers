from types import SimpleNamespace
import os
import json
import logging
import sys
from typing import List

import boto3

from botocore.exceptions import ClientError
import clients.gemini as gemini
import clients.polly as polly
import s3_wrapper
from clients.rate_limiter import RateLimiter
logger = logging.getLogger(__name__)
max_tiktok_downloads_minute = 1
class ContextCallbackHandler(object):
    geminiInst = None
    def __new__(cls):
        if not hasattr(cls, 'instance'):
             cls.instance = super(ContextCallbackHandler, cls).__new__(cls)
        cls.geminiInst = gemini.GeminiClient()
        return cls.instance
    # Common interface.
    def handle_message(self, mediaEvent) -> bool:
        if s3_wrapper.media_exists(mediaEvent.ContentLookupKey):
            return True
        return self.handle_context_generation(mediaEvent)
    
    def handle_context_generation(self, mediaEvent) -> bool:
        fileName = os.environ["SHARED_MEDIA_VOLUME_PATH"] + mediaEvent.ContentLookupKey
        
        success = s3_wrapper.upload_file(fileName, mediaEvent.ContentLookupKey)
        os.remove(fileName)
        return success
    

    def download_source_content(self, mediaEvent):
        content_type = mediaEvent.ContextMediaType
        if not RateLimiter().is_allowed("tiktok", max_tiktok_downloads_minute):
            logger.info("WARN rate limit breached for tiktok")
            return False
        pass



    def analyze_source_content(self, mediaEvent):
        pass