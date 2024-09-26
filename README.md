Media pollers will read from their respective SQS. Events trigger
requests to downstream LLMs, and results are uploaded to S3.

# Usage
Start shell environment
`pipenv shell`
`python main.py`

# Running Docker
`docker build -t poller --build-arg AwsSecretId=$AWS_ACCESS_KEY_ID --build-arg AwsSecretKey=$AWS_SECRET_ACCESS_KEY --build-arg AwsRegion=$AWS_REGION --build-arg TargetGeneration=Text .`
`docker run poller`


# Resources / Notes
Python Gemeni Vertex API: https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal
Setting service account keys: https://cloud.google.com/docs/authentication/provide-credentials-adc#local-key
- Ensure you set the localkey.json from the service account keys in project root.

