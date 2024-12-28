Media pollers will read from their respective SQS. Events trigger
requests to downstream LLMs, and results are uploaded to S3.

Should be hosted as a sidecare to containerized diffusion models.

Generally, this repository should be treated as the monolith for multimodal generation.
Lightweight processes that do not require a model such as an LLM should be included here.
For example, calls to AWS Polly, Gemini, etc are lightweight service calls; no intensive inference or generation work is done.

Note: SimpleImageGenerator was created to explore container sidecars and shared volume mounts. The calls to Lexica can and should
be added here. SimpleImageGenerator will host a dedicated stable diffusion model in the future.

# Usage
Start shell environment
`pipenv shell`
Run from pipenv: `pipenv run python.main.py` 
Run without pipenv: `python main.py`

## venvs
Creating virtual env if not present `python3 -m venv .venv`
Activate venv shell `. ./.venv/bin/activate`
Set VisualStudioCode interpreter to your .venv path.

# Running Docker
Write your current venv Pipfile to a requirements.txt for pip to use:
`pipenv run pipenv_to_requirements -f`

`docker build -t bezalel-truevine-media-consumer --build-arg AwsSecretId=$AWS_ACCESS_KEY_ID --build-arg AwsSecretKey=$AWS_SECRET_ACCESS_KEY --build-arg AwsRegion=$AWS_REGION .`
`docker run -it -e TARGET_GENERATOR="Text" -p 8080:8080 bezalel-truevine-media-consumer`

# Running Service Locally
Set envs:
SHARED_MEDIA_VOLUME_PATH="./tmp_media/"
TARGET_GENERATOR="local"
`python main.py`

If expecting volume results from another generator process, use a common path on the machine.
Set env if running locally outside container:
`export SHARED_MEDIA_VOLUME_PATH="./tmp_media/"`

# Pushing to ECR
`aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 971422718801.dkr.ecr.us-west-2.amazonaws.com`
`docker build -t bezalel-truevine-media-consumer --build-arg AwsSecretId=$AWS_ACCESS_KEY_ID --build-arg AwsSecretKey=$AWS_SECRET_ACCESS_KEY --build-arg AwsRegion=$AWS_REGION .`
`docker tag bezalel-truevine-media-consumer:latest 971422718801.dkr.ecr.us-west-2.amazonaws.com/bezalel-truevine-media-consumer:latest`
`docker push 971422718801.dkr.ecr.us-west-2.amazonaws.com/bezalel-truevine-media-consumer:latest`
# Resources / Notes
Python Gemeni Vertex API: https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal
Setting service account keys: https://cloud.google.com/docs/authentication/provide-credentials-adc#local-key
- Ensure you set the localkey.json from the service account keys in project root.

If you see two duplicate log entires when running locally, it's because there are two file handlers being used for output.

