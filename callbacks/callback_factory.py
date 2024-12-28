from .text_callback import TextCallbackHandler
from .render_callback import RenderCallbackHandler
from .image_callback import ImageCallbackHandler
from .vocal_callback import VocalCallbackHandler
from .context_callback import ContextCallbackHandler

class CallbackFactory:
    def getCallbackInstance(self, targetGenerator):
        if targetGenerator == 'Text':
            return TextCallbackHandler()
        elif targetGenerator == 'Render':
            return RenderCallbackHandler()
        elif targetGenerator == 'Image':
            return ImageCallbackHandler()
        elif targetGenerator == 'Vocal':
            return VocalCallbackHandler()
        elif targetGenerator == 'Context':
            return ContextCallbackHandler()
        else:
            raise Exception("no matching callback for targetGenerator: " + targetGenerator)