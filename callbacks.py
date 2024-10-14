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
class CallbackHandler(object):
    geminiInst = None
    targetGenerator = None
    def __new__(cls, targetGenerator):
        if not hasattr(cls, 'instance'):
             cls.instance = super(CallbackHandler, cls).__new__(cls)
        cls.targetGenerator = targetGenerator
        cls.geminiInst = gemini.GeminiClient()
        return cls.instance

    def handle_message(self, mediaEvent) -> bool:
        logger.info("MediaType: " + mediaEvent.MediaType)
        result = False
        if mediaEvent.MediaType.lower() == "text":
            result = self.handle_script_text(mediaEvent)
        if mediaEvent.MediaType.lower() == "render":
            result = self.handle_render(mediaEvent=mediaEvent)
        return result

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
        s3_wrapper.upload_file(fileName, mediaEvent.ContentLookupKey)
        os.remove(fileName)
        print("Generated conetent: " + resultText)
        return True
    
    def handle_render(self, mediaEvent) -> bool:
        if not mediaEvent.FinalRenderSequences or mediaEvent.FinalRenderSequences is None:
            print("correlationID: {0} received empty render request".format(mediaEvent.LedgerID))
            return False
        # TODO store s3 by callback id.
        # TODO will be final media aggregate in destination format by distributionFormat
        
        if mediaEvent.DistributionFormat.lower() == "blog" or mediaEvent.DistributionFormat.lower() == "integblog":
            print("correlationID: {0} calling handle final render blog".format(mediaEvent.LedgerID))
            return self.handle_final_render_blog(mediaEvent=mediaEvent)
        
        print("correlationID: {0} no matching distribution format to handle: {1}".format(mediaEvent.LedgerID,
                                                                                         mediaEvent.DistributionFormat))
        return False
    
    def handle_final_render_blog(self, mediaEvent) -> bool:
        finalBlogPayload = ""
        successfulDownload = False
        print("correlationID: {0} received sequences: {1}".format(mediaEvent.LedgerID, mediaEvent.FinalRenderSequences))
        for finalRender in mediaEvent.FinalRenderSequences:
            print("correlationID: {0} processing final render: {1}".format(mediaEvent.LedgerID, finalRender))
            if finalRender.MediaType.lower() == "text":
                successfulDownload = s3_wrapper.download_file(remote_file_name=finalRender.ContentLookupKey,
                                                              save_to_filename=mediaEvent.ContentLookupKey)
                with open(mediaEvent.ContentLookupKey, 'r') as file:
                    finalBlogPayload = file.read().replace('```json', '').replace('```', '')
                break
                
        if not successfulDownload:
            print("correlationID: {0} failed to download file: {1}".format(mediaEvent.LedgerID, finalRender.ContentLookupKey))
            return successfulDownload
        fileName = mediaEvent.ContentLookupKey + ".json"
        with open(fileName, "w") as text_file:
            text_file.write(finalBlogPayload)
        s3_wrapper.upload_file(fileName, mediaEvent.ContentLookupKey)
        os.remove(fileName)
        os.remove(mediaEvent.ContentLookupKey)
        return True