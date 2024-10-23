from types import SimpleNamespace
import os
import json
import logging
import sys

import boto3

from botocore.exceptions import ClientError
import clients.gemini as gemini
import s3_wrapper
logger = logging.getLogger(__name__)
# Used for initial scripting.
class TextCallbackHandler(object):
    geminiInst = None
    targetGenerator = None
    def __new__(cls, targetGenerator):
        if not hasattr(cls, 'instance'):
             cls.instance = super(TextCallbackHandler, cls).__new__(cls)
        cls.targetGenerator = targetGenerator
        cls.geminiInst = gemini.GeminiClient()
        return cls.instance
    # Common interface.
    def handle_message(self, mediaEvent) -> bool:
        logger.info("MediaType: " + mediaEvent.MediaType)
        return self.handle_script_text(mediaEvent)

    def handle_script_text(self, mediaEvent) -> bool:
        logger.info("SystemPromptInstruction: " + mediaEvent.SystemPromptInstruction)
        logger.info("PromptInstruction: " + mediaEvent.PromptInstruction)
        # local console
        print("SystemPromptInstruction: " + mediaEvent.SystemPromptInstruction)
        print("PromptInstruction: " + mediaEvent.PromptInstruction)
        resultText = self.geminiInst.call_model(mediaEvent.SystemPromptInstruction, mediaEvent.PromptInstruction)
        if not resultText:
            return False
        # TODO store s3 by callback id.
        fileName = mediaEvent.ContentLookupKey + ".txt"
        with open(fileName, "w") as text_file:
            text_file.write(resultText)
        success = s3_wrapper.upload_file(fileName, mediaEvent.ContentLookupKey)
        os.remove(fileName)
        print("Generated conetent: " + resultText)
        return success