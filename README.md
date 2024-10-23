Media pollers will read from their respective SQS. Events trigger
requests to downstream LLMs, and results are uploaded to S3.

# Usage
Start shell environment
`pipenv shell`
`python main.py`

## venvs
Creating virtual env if not present `python3 -m venv .venv`
Activate venv shell `. ./.venv/bin/activate`
Set VisualStudioCode interpreter to your .venv path.

# Running Docker
Write your current venv Pipfile to a requirements.txt for pip to use:
`pipenv run pipenv_to_requirements -f`

`docker build -t poller --build-arg AwsSecretId=$AWS_ACCESS_KEY_ID --build-arg AwsSecretKey=$AWS_SECRET_ACCESS_KEY --build-arg AwsRegion=$AWS_REGION .`
`docker run -it -e TARGET_GENERATOR="Text" poller`


# Resources / Notes
Python Gemeni Vertex API: https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal
Setting service account keys: https://cloud.google.com/docs/authentication/provide-credentials-adc#local-key
- Ensure you set the localkey.json from the service account keys in project root.

