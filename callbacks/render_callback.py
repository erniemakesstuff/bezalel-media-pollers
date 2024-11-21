from types import SimpleNamespace
import os
import json
import logging
import sys
from typing import List

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
             cls.geminiInst = gemini.GeminiClient()
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
        jsonStrScript = self.get_file_script_as_text(mediaEvent=mediaEvent)
        successfulDownload = jsonStrScript != ""
                
        if not successfulDownload:
            logger.info("correlationID: {0} failed to download text script file".format(mediaEvent.LedgerID))
            return successfulDownload
        
        image_urls = self.collect_any_image_urls(mediaEvent=mediaEvent)
        final_blog_payload =  json.loads(jsonStrScript, object_hook=lambda d: SimpleNamespace(**d))

        if image_urls and "blogHtml" in jsonStrScript:
            system_instruction = """Insert the following image urls as valid HTML image tags into the provided HTML payload.
                Each image url and their image tag must appear at most once.
                Each image should either preceed a header HTML tag, after a closing text paragraph, or at the end of the last paragraph.
                Images should not appear next to each other.
                Your output must be valid html.
                Image URLs to insert as HTML image tags: """ + ", ".join(image_urls)
            final_blog_payload.blogHtml = self.geminiInst.call_model(system_instruction=system_instruction, prompt_text=final_blog_payload.blogHtml)
    
        fileName = os.environ["SHARED_MEDIA_VOLUME_PATH"] + mediaEvent.ContentLookupKey + ".json"
        json_payload_str = json.dumps(final_blog_payload, indent=4, default=lambda o: o.__dict__)
        
        with open(fileName, "w") as text_file:
            text_file.write(json_payload_str)
        success = s3_wrapper.upload_file(fileName, mediaEvent.ContentLookupKey)
        os.remove(fileName)
        os.remove(mediaEvent.ContentLookupKey)
        return success
    
    def get_file_script_as_text(self, mediaEvent) -> str:
        finalBlogPayload = ""
        for finalRender in mediaEvent.FinalRenderSequences:
            if finalRender.MediaType.lower() == "text":
                successfulDownload = s3_wrapper.download_file(remote_file_name=finalRender.ContentLookupKey,
                                                              save_to_filename=mediaEvent.ContentLookupKey)
                if not successfulDownload:
                    return ""
                
                with open(mediaEvent.ContentLookupKey, 'r') as file:
                    finalBlogPayload = file.read()
                break
        return finalBlogPayload
    
    def collect_any_image_urls(self, mediaEvent) -> List[str]:
        image_urls = list()
        # E.g. https://truevine-media-storage.s3.us-west-2.amazonaws.com/Render..192d8799-84ca-4a88-8540-5965f6f76922
        object_root = "https://truevine-media-storage.s3.us-west-2.amazonaws.com/"
        for finalRender in mediaEvent.FinalRenderSequences:
            if finalRender.MediaType.lower() == "image":
                image_urls.append(object_root + finalRender.ContentLookupKey)
        return image_urls
