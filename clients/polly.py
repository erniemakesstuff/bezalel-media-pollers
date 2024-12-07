import json
from types import SimpleNamespace
import boto3
import os
import logging
from botocore.exceptions import ClientError
import botocore
session = boto3.Session(
    region_name= os.environ['AWS_REGION'],
    aws_access_key_id= os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key= os.environ['AWS_SECRET_ACCESS_KEY'],
)
logger = logging.getLogger(__name__)
polly_client = session.client('polly')

# https://docs.aws.amazon.com/polly/latest/dg/SynthesizeSpeechSamplePython.html
def create_narration(content_lookup_key, speech_text, is_male, save_as_filename) -> bool:
    voice_id = 'Salli'
    if is_male:
        voice_id = 'Matthew'
    try:
        response = polly_client.synthesize_speech(VoiceId=voice_id,
            OutputFormat='mp3', 
            Text = speech_text,
            Engine = 'standard')
        logger.info("created file: " + save_as_filename)
        with open(save_as_filename, 'wb') as file:
            file.write(response['AudioStream'].read())
    except ClientError as ex:
        logger.error("Couldn't get audio stream: " + str(ex))
        return False
    return True