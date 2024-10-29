# TODO: Replace this w/ GPU enabled container image.
# Use CUDA image? ? 
FROM --platform=linux/amd64 python:3.9-slim-bullseye 

ARG AwsSecretKey
ARG AwsSecretId
ARG AwsRegion
ENV AWS_ACCESS_KEY_ID=$AwsSecretId
ENV AWS_SECRET_ACCESS_KEY=$AwsSecretKey
ENV AWS_REGION=$AwsRegion
ENV TARGET_GENERATION="SET ME ON RUN EXEC"
 
# Creates an app directory to hold your app’s source code
WORKDIR /app
 
# Copies everything from your root directory into /app
COPY . .
RUN apt-get update
RUN apt-get install curl -y curl jq
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/* 
# --no-cache-dir
RUN pip install -r requirements.txt
RUN pip install flask
EXPOSE 8080
EXPOSE 80
EXPOSE 443
ENTRYPOINT ["sh", "./startup.sh"]