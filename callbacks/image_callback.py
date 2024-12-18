import os
import logging
import random

from clients.rate_limiter import RateLimiter
import s3_wrapper
from callbacks.common_callback import create_render
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
        if s3_wrapper.media_exists(mediaEvent.ContentLookupKey):
            return True
        return self.handle_image_generation(mediaEvent)

    def handle_image_generation(self, mediaEvent) -> bool:
        url = os.environ["SIMPLE_IMAGE_GENERATOR_ENDPOINT"]
        # Append random to deconflict file-writes to shared media volume across several processes.
        filepath_prefix = os.environ["SHARED_MEDIA_VOLUME_PATH"] + str(random.randint(0, 9999))
        request_obj = {
            "promptInstruction": mediaEvent.PromptInstruction,
            "contentLookupKey": mediaEvent.ContentLookupKey,
            "filepathPrefix": filepath_prefix
        }
        if not RateLimiter().is_allowed("lexica", 1):
            logger.info("WARN rate limit breached for lexica")
            return False
        return create_render(url, 5, request_obj, filepath_prefix, mediaEvent.ContentLookupKey)