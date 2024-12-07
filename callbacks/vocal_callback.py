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
logger = logging.getLogger(__name__)
# Final publish blogs, or videos.
class VocalCallbackHandler(object):
    def __new__(cls, targetGenerator):
        if not hasattr(cls, 'instance'):
             cls.instance = super(VocalCallbackHandler, cls).__new__(cls)
        return cls.instance
    # Common interface.
    def handle_message(self, mediaEvent) -> bool:
        if s3_wrapper.media_exists(mediaEvent.ContentLookupKey):
            return True
        return self.handle_render(mediaEvent)

    
    def handle_render(self, mediaEvent) -> bool:
        logger.info("correlationID: {0} called vocal handler".format(mediaEvent.LedgerID))
        return self.handle_vocal_generation(mediaEvent=mediaEvent)
    
    def handle_vocal_generation(self, mediaEvent) -> bool:
        is_male_vocal = "male" in mediaEvent.SystemPromptInstruction.lower()
        fileName = os.environ["SHARED_MEDIA_VOLUME_PATH"] + mediaEvent.ContentLookupKey
        success = polly.create_narration(content_lookup_key=mediaEvent.ContentLookupKey,
                               speech_text=mediaEvent.PromptInstruction, is_male=is_male_vocal,
                               save_as_filename=fileName)
        if not success:
            logger.info("correlationID: {0} failed to call AWS Polly".format(mediaEvent.LedgerID))
            return False
        
        success = s3_wrapper.upload_file(fileName, mediaEvent.ContentLookupKey)
        os.remove(fileName)
        return success