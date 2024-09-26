# Specifies a parent image
FROM python:3.13.0rc2-bookworm

ARG AwsSecretKey
ARG AwsSecretId
ARG AwsRegion
ARG TargetGeneration
ENV AWS_ACCESS_KEY_ID=$AwsSecretId
ENV AWS_SECRET_ACCESS_KEY=$AwsSecretKey
ENV AWS_REGION=$AwsRegion
ENV TARGET_GENERATION=$TargetGeneration
 
# Creates an app directory to hold your app’s source code
WORKDIR /app
 
# Copies everything from your root directory into /app
COPY . .

# TODO Install dependencies
RUN pip install
 
# Specifies the executable command that runs when the container starts
ENTRYPOINT ["sh", "./startup.sh"]