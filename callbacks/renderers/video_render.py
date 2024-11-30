import multiprocessing
from pathlib import Path
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
from moviepy import *
import numpy as np
import whisper_timestamped as whisper

logger = logging.getLogger(__name__)

class RenderClip(object):
    def __new__(cls, clip, renderMetadata, subtitles = []):
        cls.clip = clip
        cls.renderMetadata = renderMetadata
        cls.subtitles = subtitles
        return cls

class VideoRender(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(VideoRender, cls).__new__(cls)
        return cls.instance
    
    def handle_final_render_video(self, mediaEvent) -> bool:
        successful_content_download = self.download_all_content(mediaEvent.FinalRenderSequences)
        logger.info("Download status: " + str(successful_content_download))
        # Short form videos are identical to long-form videos except in two area:
        # 1) Final render resolution and aspect ratio.
        # 2) Whether subtitles are centered word-by-word.
        # TODO: call different compilation final step based on this flag.
        is_shortform = mediaEvent.DistributionFormat == 'ShortVideo'
        language = mediaEvent.Language
        video_clips = self.collect_render_clips_by_media_type(mediaEvent.FinalRenderSequences, 'Video', language)
        image_clips = self.collect_render_clips_by_media_type(mediaEvent.FinalRenderSequences, 'Image', language) # lang=> if we need to overlay text info
        narator_clips = self.collect_render_clips_by_media_type(mediaEvent.FinalRenderSequences, 'Vocal', language)
        music_clips = self.collect_render_clips_by_media_type(mediaEvent.FinalRenderSequences, 'Music', language) # lang=> songs dubbing
        sfx_clips = self.collect_render_clips_by_media_type(mediaEvent.FinalRenderSequences, 'Sfx', language)

        

        #fileName = os.environ["SHARED_MEDIA_VOLUME_PATH"] + mediaEvent.ContentLookupKey + ".json"
        #with open(fileName, "w") as text_file:
        #    text_file.write()
        #success = s3_wrapper.upload_file(fileName, mediaEvent.ContentLookupKey)
        #os.remove(fileName)
        #os.remove(mediaEvent.ContentLookupKey)
        #return success

        #self.cleanup_local_files(mediaEvent.FinalRenderSequences)
    
    def download_all_content(self, finalRenderSequences) -> bool:
        jobs = []
        statuses = []
        for s in finalRenderSequences:
            p = multiprocessing.Process(target=self.download_media, args=(s.ContentLookupKey, statuses))
            p.start()
            jobs.append(p)
        for j in jobs:
            j.join()
        
        for s in statuses:
            if not s:
                # failure detected
                return False
        return True

    def download_media(self, content_lookup_key, status):
        localFilename = os.environ["SHARED_MEDIA_VOLUME_PATH"] + content_lookup_key
        status.append( s3_wrapper.download_file(content_lookup_key, localFilename))

    def cleanup_local_files(self, final_render_sequences):
        for s in final_render_sequences:
            filename = os.environ["SHARED_MEDIA_VOLUME_PATH"] + s.ContentLookupKey
            os.remove(filename)

    def collect_render_clips_by_media_type(self, final_render_sequences, target_media_type, transcriptionLanguage = "en"):
        clips = []
        for s in final_render_sequences:
            if s.MediaType != target_media_type:
                continue

            filename = os.environ["SHARED_MEDIA_VOLUME_PATH"] + s.ContentLookupKey
            if target_media_type == 'Vocal':
                subtitles = self.get_transcribed_text(filename=filename, language=transcriptionLanguage)
                clips.append(RenderClip(clip=AudioFileClip(filename), renderMetadata=s, subtitles=subtitles))
            elif target_media_type == 'Music':
                # TODO dubbing? For music videos.
                clips.append(RenderClip(clip=AudioFileClip(filename), renderMetadata=s))
            elif target_media_type == 'Sfx':
                clips.append(RenderClip(clip=AudioFileClip(filename), renderMetadata=s))
            elif target_media_type == 'Video':
                clips.append(RenderClip(clip=VideoFileClip(filename), renderMetadata=s))
            elif target_media_type == 'Image':
                # TODO overlay text? Probably not.
                clips.append(RenderClip(clip=ImageClip(filename), renderMetadata=s))
            else:
                raise Exception('unsupported media type to moviepy clip')

        return clips

    # Ref: https://www.angel1254.com/blog/posts/word-by-word-captions
    # Note: this should be done FIRST for narrator clips to avoid file moviepy clip file locks.
    def get_transcribed_text(self, filename, language):
        audio = whisper.load_audio(filename)
        model = whisper.load_model("tiny") # tiny, base, small, medium, large
        results = whisper.transcribe(model, audio, language=language)

        return results["segments"]
    
    def get_total_duration(clips):
        seconds = 0
        for c in clips:
            seconds += c.duration
        return seconds
    
    def get_video_title(self, final_render_sequences) -> str:
        title = "A great video!"
        for s in final_render_sequences:
            if s.MediaType != 'Text' and s.PositionLayer == 'HiddenScript':
                # no need to downlaod from s3; handled by download_all in previous call
                # defer cleanup
                local_file_name = os.environ["SHARED_MEDIA_VOLUME_PATH"] + s.ContentLookupKey
                with open(local_file_name, 'r') as file:
                    payload = file.read()
                script = json.loads(payload)
                title = script.videoTitle
                break

        return title
    
    def perform_render(is_short_form, video_title,
                       image_clips,
                       video_clips,
                       vocal_clips,
                       music_clips,
                       sfx_clips,
                       watermark_text,
                       local_save_as) -> bool:
        max_length_short_video_sec = 59
        # If clipFile is prefixed with b --> mute.
        # Otherwise, reduce background clip volume by 30%
        # TODO: separate logic for music videos
        is_music_video = len(vocal_clips) == 0 and len(music_clips) > 0
        

        # TODO watermark
        return True
    
    def create_visual_layer(self, image_clips, video_clips):
        visual_clips = []
        clipIter = ""
        # TODO: Group and order by PositionLayer + RenderSequence
        # Sequence full-screen content first
        # Then sequence partials overlaying
        for i in image_clips:
            image_duration_sec = 2
            i.duration(image_duration_sec)
            visual_clips.append(i)
        return visual_clips