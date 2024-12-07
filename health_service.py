import json
import logging
import os
from flask import Flask
import queue_wrapper
from callbacks.renderers import video_render
app = Flask(__name__)
logger = logging.getLogger(__name__)
@app.route("/health")
def health_check():
    return "Healthy"


@app.route("/test")
def testRender():
    finalRenderEvent = {
        "LedgerID": "6cdc973c-5b57-4a64-b1ce-41ead40f7c51",
        "PromptInstruction": "OriginalPromptHash: 0096c1ab79e2f7fe9c4aa02ed5562981 - MetaDescriptor: FinalRender - OPT_PUB: YouTubeTest",
        "SystemPromptInstruction": "OriginalPromptHash: 0096c1ab79e2f7fe9c4aa02ed5562981 - MetaDescriptor: FinalRender - OPT_PUB: YouTubeTest",
        "MediaType": "Render",
        "DistributionFormat": "ShortVideo",
        "ContentLookupKey": "Render.6cdc973c-5b57-4a64-b1ce-41ead40f7c51.a3e5b5ed-2e64-4f5c-a6c0-11b7a16cd6d7.render",
        "Niche": "Drama",
        "Language": "EN",
        "PromptHash": "c110ddc74a8ca6030ebdc8ca293c31c0",
        "EventID": "EN.Render.Drama.c110ddc74a8ca6030ebdc8ca293c31c0",
        "ParentEventID": "EN.Text.Drama.0096c1ab79e2f7fe9c4aa02ed5562981",
        "PositionLayer": "",
        "RenderSequence": 0,
        "FinalRenderSequences": "[{\"EventID\":\"EN.Text.Drama.0096c1ab79e2f7fe9c4aa02ed5562981\",\"MediaType\":\"Text\",\"PositionLayer\":\"HiddenScript\",\"ContentLookupKey\":\"Text.6cdc973c-5b57-4a64-b1ce-41ead40f7c51.67325c98-ae5f-4bb9-99e7-0c018cf4b258.json\",\"RenderSequence\":-1},{\"EventID\":\"EN.Image.Drama.a94639be8367965abe9d105e86a181ec\",\"MediaType\":\"Image\",\"PositionLayer\":\"Thumbnail\",\"ContentLookupKey\":\"Image.6cdc973c-5b57-4a64-b1ce-41ead40f7c51.f9f9927a-1760-48f2-80ff-709ff9d6aa2e.png\",\"RenderSequence\":0},{\"EventID\":\"EN.Music.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Music\",\"PositionLayer\":\"BackgroundMusic\",\"ContentLookupKey\":\"m6.mp3\",\"RenderSequence\":0},{\"EventID\":\"EN.Vocal.Drama.6e32fb95c91915df92962c7e0d8d923c\",\"MediaType\":\"Vocal\",\"PositionLayer\":\"Narrator\",\"ContentLookupKey\":\"Vocal.6cdc973c-5b57-4a64-b1ce-41ead40f7c51.9c0f1694-797f-4c4d-90ba-876c67f2eb0d.mp3\",\"RenderSequence\":0},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"ContentLookupKey\":\"b32.mp4\",\"RenderSequence\":1},{\"EventID\":\"EN.Vocal.Drama.f8b53ea5d276a8a744c7e6b22439710e\",\"MediaType\":\"Vocal\",\"PositionLayer\":\"Narrator\",\"ContentLookupKey\":\"Vocal.6cdc973c-5b57-4a64-b1ce-41ead40f7c51.ae437c1e-d15e-4759-a688-e91d1f3a39c3.mp3\",\"RenderSequence\":1},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"ContentLookupKey\":\"b52.mp4\",\"RenderSequence\":2},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"ContentLookupKey\":\"b54.mp4\",\"RenderSequence\":3},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"ContentLookupKey\":\"b10.mp4\",\"RenderSequence\":4},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"ContentLookupKey\":\"b21.mp4\",\"RenderSequence\":5}]",
        "WatermarkText": "TrueVineMedia",
        "RestrictToPublisherID": "YouTubeTest",
        "MetaMediaDescriptor": "FinalRender"
    }
    mediaEvent = queue_wrapper.to_media_event(json.dumps(finalRenderEvent))

    renderer = video_render.VideoRender()
    logger.info("calling video render")
    return str(renderer.handle_final_render_video(mediaEvent=mediaEvent))