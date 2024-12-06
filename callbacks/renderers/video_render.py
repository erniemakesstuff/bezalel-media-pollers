import copy
import math
import multiprocessing
from pathlib import Path
import random
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
        successful_content_download = self.__download_all_content(mediaEvent.FinalRenderSequences)
        if not successful_content_download:
            logger.error("correlationId {0} failed to download media files for rendering".format(mediaEvent.LedgerID))
            return False
        is_shortform = mediaEvent.DistributionFormat == 'ShortVideo'
        language = mediaEvent.Language
        
        thumbnail_text = self.__get_thumbnail_text(mediaEvent.FinalRenderSequences)
        local_file_name = os.environ["SHARED_MEDIA_VOLUME_PATH"] + mediaEvent.ContentLookupKey + ".mp4"
        # Creating as a separate process because moviepy exits the thread after writing compiled video.
        
        #render_process = multiprocessing.Process(target=self.__perform_render, args=(
        #    is_shortform, thumbnail_text, mediaEvent.FinalRenderSequences, language, "TrueVineMedia", local_file_name))
        #render_process.start()
        #render_process.join()
        # TODO: Change this to wait-for-file
        if not Path(local_file_name).is_file():
            return False
        success = s3_wrapper.upload_file(local_file_name, mediaEvent.ContentLookupKey)
        
        self.__cleanup_local_files(mediaEvent.FinalRenderSequences)
        rendered_media_path = Path(local_file_name)
        if rendered_media_path.is_file():
            os.remove(local_file_name)
        tmp_lookupkey = Path(mediaEvent.ContentLookupKey)
        if tmp_lookupkey.is_file():
            os.remove(mediaEvent.ContentLookupKey)
        return success

        
    
    def __download_all_content(self, finalRenderSequences) -> bool:
        jobs = []
        with multiprocessing.Manager() as manager:
            statuses = manager.list()
            for s in finalRenderSequences:
                p = multiprocessing.Process(target=self.__download_media, args=(s.ContentLookupKey, statuses))
                p.start()
                jobs.append(p)
            for j in jobs:
                j.join()
            
            if len(statuses) == 0:
                logger.error("no download statuses reported")
                return False
            for s in statuses:
                if not s:
                    # failure detected
                    return False
        return True

    def __download_media(self, content_lookup_key, status):
        localFilename = os.environ["SHARED_MEDIA_VOLUME_PATH"] + content_lookup_key
        path = Path(localFilename)
        if path.is_file():
            # already exists, return
            status.append(True)
            return
        status.append(s3_wrapper.download_file(content_lookup_key, localFilename))

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