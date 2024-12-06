FROM --platform=linux/amd64 python:3.9-slim-bullseye 

ARG AwsSecretKey
ARG AwsSecretId
ARG AwsRegion
ENV AWS_ACCESS_KEY_ID=$AwsSecretId
ENV AWS_SECRET_ACCESS_KEY=$AwsSecretKey
ENV AWS_REGION=$AwsRegion
ENV TARGET_GENERATION="SET ME ON RUN EXEC"
# TODO: Set volume mount path for sidecars.
ENV SHARED_MEDIA_VOLUME_PATH="./tmp_media/"
ENV GOOGLE_APPLICATION_CREDENTIALS="./localkey.json"
ENV SIMPLE_IMAGE_GENERATOR_ENDPOINT="http://localhost:5051/image"
ENV VIDEO_RENDERER_ENDPOINT="http://localhost:5052/image"
# Creates an app directory to hold your app’s source code
WORKDIR /app
 
# Copies everything from your root directory into /app
COPY . .
RUN apt-get clean
RUN apt-get update
RUN apt update
RUN apt-get install curl -y curl jq
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/* 

# --no-cache-dir
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install flask
EXPOSE 8080
EXPOSE 80
EXPOSE 443
ENTRYPOINT ["./startup.sh"]