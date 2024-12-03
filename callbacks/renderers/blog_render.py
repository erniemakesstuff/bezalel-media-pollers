from pathlib import Path
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

class BlogRender(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(BlogRender, cls).__new__(cls)
            cls.geminiInst = gemini.GeminiClient()
        return cls.instance
    
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
        path_content = Path(mediaEvent.ContentLookupKey)
        if path_content.is_file():
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
