from .text_callback import TextCallbackHandler
from .render_callback import RenderCallbackHandler
from .image_callback import ImageCallbackHandler

class CallbackFactory:
    def getCallbackInstance(self, targetGenerator):
        if targetGenerator == 'Text':
            return TextCallbackHandler(targetGenerator=targetGenerator)
        elif targetGenerator == 'Render':
            return RenderCallbackHandler(targetGenerator=targetGenerator)
        elif targetGenerator == 'Image':
            return ImageCallbackHandler(targetGenerator=targetGenerator)
        else:
            raise Exception("no matching callback for targetGenerator: " + targetGenerator)