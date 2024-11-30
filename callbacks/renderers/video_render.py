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
    def __init__(self, clip, render_metadata, subtitles = []):
        self.clip = clip
        self.render_metadata = render_metadata
        self.subtitles = subtitles

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
        
        video_title = self.get_video_title(mediaEvent.FinalRenderSequences)
        self.perform_render(is_short_form=is_shortform, video_title=video_title,
                            language=language,
                            final_render_sequences=mediaEvent.FinalRenderSequences,
                            watermark_text="TrueVineMedia",
                            local_save_as="testVideo.mp4")

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
        if os.path(localFilename):
            # already exists, return
            status.append(True)
            return
        status.append(s3_wrapper.download_file(content_lookup_key, localFilename))

    def cleanup_local_files(self, final_render_sequences):
        for s in final_render_sequences:
            filename = os.environ["SHARED_MEDIA_VOLUME_PATH"] + s.ContentLookupKey
            os.remove(filename)

    def collect_render_clips_by_media_type(self, final_render_sequences, target_media_type, transcriptionLanguage = "en"):
        clips = list()
        for s in final_render_sequences:
            if s.MediaType != target_media_type:
                continue

            filename = os.environ["SHARED_MEDIA_VOLUME_PATH"] + s.ContentLookupKey
            if s.MediaType == 'Vocal':
                subtitles = self.get_transcribed_text(filename=filename, language=transcriptionLanguage)
                clips.append(RenderClip(clip=AudioFileClip(filename), render_metadata=s, subtitles=subtitles))
            elif s.MediaType == 'Music':
                #return clips
                # TODO dubbing? For music videos.
                clips.append(RenderClip(clip=AudioFileClip(filename), render_metadata=s))
            elif s.MediaType == 'Sfx':
                #return clips
                clips.append(RenderClip(clip=AudioFileClip(filename), render_metadata=s))
            elif s.MediaType == 'Video':
                clips.append(RenderClip(clip=VideoFileClip(filename), render_metadata=s))
            elif target_media_type == 'Image':
                # TODO overlay text? Probably not.
                clips.append(RenderClip(clip=ImageClip(filename), render_metadata=s))
            elif target_media_type == 'Text':
                return clips
                # TODO: Need to unpack this first to raw-text, not json.
                #clips.append(RenderClip(clip=TextClip(filename), render_metadata=s))
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
    
    def perform_render(self, is_short_form, video_title,
                       final_render_sequences,
                       language,
                       watermark_text,
                       local_save_as) -> bool:
        video_clips = self.collect_render_clips_by_media_type(final_render_sequences, 'Video', language)
        image_clips = self.collect_render_clips_by_media_type(final_render_sequences, 'Image', language) # lang=> if we need to overlay text info
        vocal_clips = self.collect_render_clips_by_media_type(final_render_sequences, 'Vocal', language)
        music_clips = self.collect_render_clips_by_media_type(final_render_sequences, 'Music', language) # lang=> songs dubbing
        sfx_clips = self.collect_render_clips_by_media_type(final_render_sequences, 'Sfx', language)
        # TODO: Support text clips
        #text_clips = self.collect_render_clips_by_media_type(final_render_sequences, 'Text', language)

        max_length_short_video_sec = 59
        # If clipFile is prefixed with b --> mute.
        # Otherwise, reduce background clip volume by 30%
        # TODO: separate logic for music videos
        is_music_video = len(vocal_clips) == 0 and len(music_clips) > 0
        # TODO reduce background music 30%.


        visual_layer = self.__create_visual_layer(image_clips=image_clips, video_clips=video_clips)
        audio_layer = self.__create_audio_layer(vocal_clips, music_clips, sfx_clips)
        
        composite_video = CompositeVideoClip(np.array(
            self.__collect_moviepy_clips(visual_layer)))
        composite_audio = CompositeAudioClip(np.array(
            self.__collect_moviepy_clips(audio_layer)
        ))
        composite_video.preview(fps=10)
        # TODO watermark
        return True
    
    def __create_visual_layer(self, image_clips, video_clips):
        # TODO: Group and order by PositionLayer + RenderSequence
        # Sequence full-screen content first.
        # Then sequence partials overlaying.
        self.__set_image_clips_duration(image_clips=image_clips, duration_sec=2)
        visual_clips = image_clips + video_clips
        self.__combine_sequences(layer_clips=visual_clips)
        # TODO: other position layers.
        # TODO: ensure close all moviepy clips.
        return visual_clips
    
    def __create_audio_layer(self, vocal_clips, music_clips, sfx_clips):
        audio_layer = vocal_clips + sfx_clips
        self.__combine_sequences(audio_layer)

        # contiguous background_music
        self.__combine_sequences(music_clips)
        return audio_layer + music_clips
    
    def __set_image_clips_duration(self, image_clips, duration_sec):
        for i, ic in enumerate(image_clips):
            image_clips[i].clip = image_clips[i].clip.with_duration(duration_sec)

    def __combine_sequences(self, layer_clips):
        # allocate grouping by sequence numbers
        sequenceNumberToClipsList = {}

        for rclip in layer_clips:
            render_sequence = rclip.render_metadata.RenderSequence
            if render_sequence not in sequenceNumberToClipsList:
                sequenceNumberToClipsList[render_sequence] = []
            
            sequenceNumberToClipsList[render_sequence].append(rclip)
        
        # assign start times
        for i, rclip in enumerate(layer_clips):
            render_sequence = rclip.render_metadata.RenderSequence
            prev_render_sequence = render_sequence - 1
            if prev_render_sequence in sequenceNumberToClipsList:
                clips_in_prev_sequence = sequenceNumberToClipsList[prev_render_sequence]
                max_end_clip = self.__get_longest_render_clip(clips_in_prev_sequence)
                layer_clips[i].clip = rclip.clip.with_start(max_end_clip.clip.end)

    def __get_longest_render_clip(self, clips):
        max_dur_clip = clips[0]
        for rc in clips:
            if rc.clip.duration > max_dur_clip.clip.duration:
                max_dur_clip = rc
        return max_dur_clip
        
    def __collect_moviepy_clips(self, render_clips):
        movie_clips = []
        for r in render_clips:
            movie_clips.append(r.clip)
        return movie_clips
    
    def set_background_audio_on_visual_clips(self, visual_clips):
        #for v in visual_clips:
        #    AudioFileClip().with_effects(afx.)
        #    VideoFileClip().with_effects()
        return True