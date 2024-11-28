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
             cls.geminiInst = gemini.GeminiClient()
        return cls.instance
    # Common interface.
    def handle_message(self, mediaEvent) -> bool:
        if s3_wrapper.media_exists(mediaEvent.ContentLookupKey):
            return True
        return self.handle_render(mediaEvent)

    
    def handle_render(self, mediaEvent) -> bool:
        if not mediaEvent.FinalRenderSequences or mediaEvent.FinalRenderSequences is None:
            logger.info("correlationID: {0} received empty render request".format(mediaEvent.LedgerID))
            return False
        
        return self.handle_vocal_generation(mediaEvent=mediaEvent)
    
    def handle_vocal_generation(self, mediaEvent) -> bool:
        is_male_vocal = "male" in mediaEvent.SystemPromptInstruction.lower()
        success = polly.create_narration(content_lookup_key=mediaEvent.ContentLookupKey,
                               speech_text=mediaEvent.PromptInstruction, is_male=is_male_vocal)
        if not success:
            logger.info("correlationID: {0} failed to call AWS Polly".format(mediaEvent.LedgerID))
            return False
        
        fileName = os.environ["SHARED_MEDIA_VOLUME_PATH"] + mediaEvent.ContentLookupKey
        success = s3_wrapper.upload_file(fileName, mediaEvent.ContentLookupKey)
        os.remove(fileName)
        return success