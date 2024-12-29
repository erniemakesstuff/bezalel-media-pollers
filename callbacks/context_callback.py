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
import clients.polly as polly
import s3_wrapper
from clients.rate_limiter import RateLimiter
from clients.video_downloader import VideoDownloader
from clients.image_downloader import ImageDownloader
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
max_image_downloads_minute = 1
max_video_downloads_minute = 1

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
        # TODO https://trello.com/c/aADouL3V
        # ...
        downloaded_remote_file = self.download_source_content(mediaEvent)
        if not downloaded_remote_file:
            logger.error("failed to download remote files from context handler")
            return False
        

        success = s3_wrapper.upload_file(fileName, mediaEvent.ContentLookupKey)
        os.remove(fileName)
        return success
    

    def download_source_content(self, mediaEvent):
        content_type = mediaEvent.ContextMediaType
        successful_download = False
        if content_type == 'Image':
            successful_download = self.download_image(mediaEvent)
        elif content_type == 'Video':
            successful_download = self.download_video(mediaEvent)
        
        return successful_download

    def download_image(self, mediaEvent) -> bool:
        if Path(os.environ["SHARED_MEDIA_VOLUME_PATH"] + mediaEvent.ContextSourceLookupKey).is_file():
            return True
        
        base_url = self.extract_base_url(mediaEvent.ContextSourceUrl)
        if not RateLimiter().is_allowed(base_url, max_image_downloads_minute):
            logger.info("WARN rate limit breached for " + base_url)
            return False
        
        return ImageDownloader().download_image(
            img_url=mediaEvent.ContextSourceUrl,
            directory_savepath=os.environ["SHARED_MEDIA_VOLUME_PATH"],
            save_as_filename=mediaEvent.ContextSourceLookupKey
        )
    
    def download_video(self, mediaEvent) -> bool:
        filename = os.environ["SHARED_MEDIA_VOLUME_PATH"] + mediaEvent.ContextSourceLookupKey
        if Path(filename).is_file():
            return True
        
        base_url = self.extract_base_url(mediaEvent.ContextSourceUrl)
        if not RateLimiter().is_allowed(base_url, max_video_downloads_minute):
            logger.info("WARN rate limit breached for " + base_url)
            return False
        
        return VideoDownloader().download_video(
            video_url=mediaEvent.ContextSourceUrl,
            save_as=filename
        )
    
    def analyze_source_content(self, mediaEvent):
        self.geminiInst.call_model_json_out
        pass

    def extract_base_url(self, url):
        """
        Extracts the base URL from a given URL.

        Args:
            url: The URL string.

        Returns:
            The base URL string, or None if the URL is invalid.
        """
        try:
            parsed_url = urlparse(url)
            # Reconstruct base URL
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            return base_url
        except Exception:
            return None