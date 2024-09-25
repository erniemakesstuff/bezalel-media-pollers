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
        self.model = GenerativeModel("gemini-1.5-flash-001")

  def call_model(self):
    response = self.model.generate_content(
        "What's a good name for a flower shop that specializes in selling bouquets of dried flowers?"
    )

    print(response.text)