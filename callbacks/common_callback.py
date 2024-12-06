from pathlib import Path
from types import SimpleNamespace
import os
import json
import logging
from urllib.parse import urlencode
import requests
import time

from botocore.exceptions import ClientError
import s3_wrapper
logger = logging.getLogger(__name__)
def request_and_wait(url, max_wait_iterations, request_dict, content_lookup_key) -> bool:
        headers = {'Accept': '*/*',
        'Content-Type': 'application/json' }
        result = requests.post(url, json.dumps(request_dict), verify=False, timeout=180, headers=headers)
        if not result.ok:
            logger.error("failed to call generator: " + result.reason)
            return False
        
        # TODO store s3 by callback id if integrating with third-party apis.
        fileName = os.environ["SHARED_MEDIA_VOLUME_PATH"] + content_lookup_key

        # wait for the file to be ready
        max_wait_iterations = max_wait_iterations
        wait_iteration = 1
        while not os.path.exists(fileName) and wait_iteration <= max_wait_iterations:
            logger.info("Waiting for file to be created: " + fileName)
            time.sleep(60)
            wait_iteration += 1

        if not os.path.exists(fileName):
            logger.info("File was not generated; timeout: " + fileName)
            return False
        logger.info("file created: " + fileName)
        success = s3_wrapper.upload_file(fileName, content_lookup_key)
        if success and Path(fileName).is_file():
            os.remove(fileName)
        logger.info("Generated conetent: " + fileName)
        return success