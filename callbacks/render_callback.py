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
# Final publish blogs, or videos.
class RenderCallbackHandler(object):
    blogDistributionFormats = [
        "blog", "tinyblog", "integblog"
    ]
    def __new__(cls, targetGenerator):
        if not hasattr(cls, 'instance'):
             cls.instance = super(RenderCallbackHandler, cls).__new__(cls)
        return cls.instance
    # Common interface.
    def handle_message(self, mediaEvent) -> bool:
        logger.info("MediaType: " + mediaEvent.MediaType)
        if s3_wrapper.media_exists(mediaEvent.ContentLookupKey):
            return True
        return self.handle_render(mediaEvent)

    
    def handle_render(self, mediaEvent) -> bool:
        if not mediaEvent.FinalRenderSequences or mediaEvent.FinalRenderSequences is None:
            logger.info("correlationID: {0} received empty render request".format(mediaEvent.LedgerID))
            return False
        # TODO store s3 by callback id.
        # TODO will be final media aggregate in destination format by distributionFormat
        if mediaEvent.DistributionFormat.lower() in self.blogDistributionFormats:
            logger.info("correlationID: {0} calling handle final render blog".format(mediaEvent.LedgerID))
            return self.handle_final_render_blog(mediaEvent=mediaEvent)
        
        logger.info("correlationID: {0} no matching distribution format to handle: {1}".format(mediaEvent.LedgerID,
                                                                                         mediaEvent.DistributionFormat))
        return False
    
    def handle_final_render_blog(self, mediaEvent) -> bool:
        finalBlogPayload = ""
        successfulDownload = False
        for finalRender in mediaEvent.FinalRenderSequences:
            if finalRender.MediaType.lower() == "text":
                successfulDownload = s3_wrapper.download_file(remote_file_name=finalRender.ContentLookupKey,
                                                              save_to_filename=mediaEvent.ContentLookupKey)
                if not successfulDownload:
                    return successfulDownload
                
                with open(mediaEvent.ContentLookupKey, 'r') as file:
                    finalBlogPayload = file.read().replace('```json', '').replace('```', '')
                break
                
        if not successfulDownload:
            logger.info("correlationID: {0} failed to download file: {1}".format(mediaEvent.LedgerID, finalRender.ContentLookupKey))
            return successfulDownload
        fileName = os.environ["SHARED_MEDIA_VOLUME_PATH"] + mediaEvent.ContentLookupKey + ".json"
        with open(fileName, "w") as text_file:
            text_file.write(finalBlogPayload)
        success = s3_wrapper.upload_file(fileName, mediaEvent.ContentLookupKey)
        os.remove(fileName)
        os.remove(mediaEvent.ContentLookupKey)
        return success