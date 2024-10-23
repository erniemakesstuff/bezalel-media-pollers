from .text_callback import TextCallbackHandler
from .render_callback import RenderCallbackHandler

class CallbackFactory:
    def getCallbackInstance(self, targetGenerator):
        if targetGenerator == 'Text':
            return TextCallbackHandler(targetGenerator=targetGenerator)
        elif targetGenerator == 'Render':
            return RenderCallbackHandler(targetGenerator=targetGenerator)
        else:
            raise Exception("no matching callback for targetGenerator: " + targetGenerator)