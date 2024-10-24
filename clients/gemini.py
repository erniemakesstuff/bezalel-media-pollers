import json
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting

class GeminiClient(object):
    model = None
    safety_config = [
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        ),
       SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY,
            threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_UNSPECIFIED,
            threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        ),
    ]
    def __new__(cls):
        if not hasattr(cls, 'instance'):
             cls.instance = super(GeminiClient, cls).__new__(cls)
        return cls.instance
    def __init__(self):
        vertexai.init(project="three-doors-422720", location="us-west1")
    # API Docs: https://cloud.google.com/vertex-ai/generative-ai/docs/reference/python/latest
    def call_model(self, system_instruction, prompt_text) -> str:
        self.model = GenerativeModel("gemini-1.5-flash-001",
                                 system_instruction=system_instruction,
                                 safety_settings=self.safety_config)
        response = self.model.generate_content(
            prompt_text
            )
        return self.sanitize_json(respText=response.text, retryCount=0)
    
    def sanitize_json(self, respText, retryCount) ->str:
        maxRetries = 3
        if retryCount > maxRetries:
            return Exception("max retries exceeded for sanitizing json")
        isValidJson = self.parse(respText)
        if isValidJson:
            return respText
        print("Detected invalid json")
        jsonInstruction = """
            The following input is invalid json.
            You will transform the input into valid json, and
            return syntactically correct json.
            ###
        """
        self.model = GenerativeModel("gemini-1.5-flash-001",
                                 system_instruction=jsonInstruction,
                                 safety_settings=self.safety_config)
        response = self.model.generate_content(
            respText
            )
        isValidJson = self.parse(response.text)
        if isValidJson:
            return response.text
        return self.sanitize_json(respText=response.text, retryCount=retryCount+1)
    
    def parse(self, text) -> bool:
        try:
            contents = text.replace('```json', '').replace('```', '')
            json.loads(contents)
            return True
        except ValueError as e:
            return False