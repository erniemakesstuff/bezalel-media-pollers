import vertexai
from vertexai.generative_models import GenerativeModel

class GeminiClient(object):
    model = None
    def __new__(cls):
        if not hasattr(cls, 'instance'):
             cls.instance = super(GeminiClient, cls).__new__(cls)
        return cls.instance
    def __init__(self):
        vertexai.init(project="three-doors-422720", location="us-west1")
    # API Docs: https://cloud.google.com/vertex-ai/generative-ai/docs/reference/python/latest
    def call_model(self, system_instruction, prompt_text) -> str:
        self.model = GenerativeModel("gemini-1.5-flash-001",
                                 system_instruction=system_instruction)
        response = self.model.generate_content(
            prompt_text
            )
        print(response.text)
        return response.text