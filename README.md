Media pollers will read from their respective SQS. Events trigger
requests to downstream LLMs, and results are uploaded to S3.

# Usage
Start shell environment
`pipenv shell`
`python main.py`


# Resources / Notes
Python Gemeni Vertex API: https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal
Setting service account keys: https://cloud.google.com/docs/authentication/provide-credentials-adc#local-key

