import copy
import math
import multiprocessing
from pathlib import Path
import random
import time
from types import SimpleNamespace
import os
import json
import logging
import sys
from typing import List
import s3_wrapper
import boto3

from botocore.exceptions import ClientError
import clients.gemini as gemini
import s3_wrapper
from callbacks.common_callback import create_render
logger = logging.getLogger(__name__)

class RenderClip(object):
    def __init__(self, clip, render_metadata, subtitle_segments = []):
        self.clip = clip
        self.render_metadata = render_metadata
        self.subtitle_segments = subtitle_segments

class VideoRender(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(VideoRender, cls).__new__(cls)
        return cls.instance
    
    def handle_final_render_video(self, mediaEvent) -> bool:
        logger.debug("correlationId {0} downloading all content".format(mediaEvent.LedgerID))
        successful_content_download = self.__download_all_content(mediaEvent.FinalRenderSequences)
        
        if not successful_content_download:
            logger.error("correlationId {0} failed to download media files for rendering".format(mediaEvent.LedgerID))
            return False
        logger.debug("correlationId {0} all content downloaded".format(mediaEvent.LedgerID))
        # Sleep to avoid race-condition between files downloaded, and sidecar doesn't see the file.
        # Files are already downloaded at this point, PRIOR to calling sidecar, but sidecar doesn't see it
        # for whatever reason.
        time.sleep(10)
        is_shortform = mediaEvent.DistributionFormat == 'ShortVideo'
        language = mediaEvent.Language
        thumbnail_text = self.__get_thumbnail_text(mediaEvent.FinalRenderSequences)
        watermark_text = "TrueVineMedia"
        if len(mediaEvent.WatermarkText) != 0:
            watermark_text = mediaEvent.WatermarkText
        def get_obj_dict(obj):
            return obj.__dict__
        request_obj = {
            "isShortForm": is_shortform,
            "finalRenderSequences": json.dumps(mediaEvent.FinalRenderSequences, default=get_obj_dict),
            "language": language,
            "watermarkText": watermark_text,
            "thumbnailText": thumbnail_text,
            "contentLookupKey": mediaEvent.ContentLookupKey,
        }
        
        # Creating as a separate process because moviepy exits the thread after writing compiled video.
        success = create_render(url=os.environ["VIDEO_RENDERER_ENDPOINT"], max_wait_iterations=20,
                                                   request_dict=request_obj, content_lookup_key=mediaEvent.ContentLookupKey)
        self.__cleanup_local_files(mediaEvent.FinalRenderSequences)
        if Path(mediaEvent.ContentLookupKey).is_file():
            os.remove(mediaEvent.ContentLookupKey)
        return success

        
    
    def __download_all_content(self, finalRenderSequences) -> bool:
        jobs = []
        with multiprocessing.Manager() as manager:
            statuses = manager.list()
            for s in finalRenderSequences:
                p = multiprocessing.Process(target=self.__download_media, args=(s.ContentLookupKey, statuses))
                jobs.append(p)
                p.start()

            for j in jobs:
                j.join()
            
            if len(statuses) == 0:
                logger.error("no download statuses reported")
                return False
            for s in statuses:
                index_success_flag = 0
                index_file = 1
                if not s[index_success_flag]:
                    logger.error("failure status reported: " + s[index_file])
                    # failure detected
                    return False
        return True

    def __download_media(self, content_lookup_key, status):
        localFilename = os.environ["SHARED_MEDIA_VOLUME_PATH"] + content_lookup_key
        path = Path(localFilename)
        if path.is_file():
            # already exists, return
            status.append([True, content_lookup_key])
            return
        
        status.append([s3_wrapper.download_file(content_lookup_key, localFilename), content_lookup_key])

    def __cleanup_local_files(self, final_render_sequences):
        for s in final_render_sequences:
            filename = os.environ["SHARED_MEDIA_VOLUME_PATH"] + s.ContentLookupKey
            file_path = Path(filename)
            if file_path.is_file():
                os.remove(filename)

    
    def __get_thumbnail_text(self, final_render_sequences) -> str:
        thumbnail_text = "A great video!"
        for s in final_render_sequences:
            if s.MediaType == 'Text' and s.PositionLayer == 'HiddenScript':
                # no need to downlaod from s3; handled by download_all in previous call
                # defer cleanup
                local_file_name = os.environ["SHARED_MEDIA_VOLUME_PATH"] + s.ContentLookupKey
                with open(local_file_name, 'r') as file:
                    payload = file.read()
                script = json.loads(payload)
                thumbnail_text = script['videoTitle']
                if 'videoThumbnailText' in script:
                    thumbnail_text = script['videoThumbnailText']
                break

        return thumbnail_text