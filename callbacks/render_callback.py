import logging
import clients.gemini as gemini
from callbacks.renderers import blog_render, video_render
import s3_wrapper
logger = logging.getLogger(__name__)
# Final publish blogs, or videos.
class RenderCallbackHandler(object):
    blogDistributionFormats = [
        "blog", "tinyblog", "integblog"
    ]
    videoDistributionFormats = [
        "shortvideo"
    ]
    def __new__(cls):
        if not hasattr(cls, 'instance'):
             cls.instance = super(RenderCallbackHandler, cls).__new__(cls)
             cls.geminiInst = gemini.GeminiClient()
             cls.blogRender = blog_render.BlogRender()
             cls.video_renderer = video_render.VideoRender()
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
        if mediaEvent.DistributionFormat.lower() in self.blogDistributionFormats:
            logger.info("correlationID: {0} calling handle final render blog".format(mediaEvent.LedgerID))
            return self.blogRender.handle_final_render_blog(mediaEvent=mediaEvent)
        elif mediaEvent.DistributionFormat.lower() in self.videoDistributionFormats:
            logger.info("correlationID: {0} calling handle final render video".format(mediaEvent.LedgerID))
            return self.video_renderer.handle_final_render_video(mediaEvent)
        
        logger.error("correlationID: {0} no matching distribution format to handle: {1}".format(mediaEvent.LedgerID,
                                                                                         mediaEvent.DistributionFormat))
        return False
    