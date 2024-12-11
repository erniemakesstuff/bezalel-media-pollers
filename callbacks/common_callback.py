from pathlib import Path
import os
import json
import logging
import requests
import time

import s3_wrapper
logger = logging.getLogger(__name__)
def create_render(url, max_wait_iterations, request_dict, filepath_prefix, content_lookup_key) -> bool:
        headers = {'Accept': '*/*',
        'Content-Type': 'application/json' }
        result = requests.post(url, json.dumps(request_dict), verify=False, timeout=180, headers=headers)
        if not result.ok:
            logger.error("failed to call generator: " + result.reason)
            return False
        
        fileName = filepath_prefix + content_lookup_key

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
        logger.info("Generated and uploaded conetent: " + fileName)
        return success