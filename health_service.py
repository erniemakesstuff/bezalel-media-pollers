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
    "LedgerID": "77fad92d-4d17-469c-aa39-62c3c55138e8",
    "PromptInstruction": "OriginalPromptHash: 1de60ef338c2c6e4e88af012b82596d7 - MetaDescriptor: FinalRender - OPT_PUB: YoutubeProfile1",
    "SystemPromptInstruction": "OriginalPromptHash: 1de60ef338c2c6e4e88af012b82596d7 - MetaDescriptor: FinalRender - OPT_PUB: YoutubeProfile1",
    "MediaType": "Render",
    "DistributionFormat": "ShortVideo",
    "ContentLookupKey": "Render.77fad92d-4d17-469c-aa39-62c3c55138e8.955ad0ae-0bd5-48d2-baa2-4192c5581c7e.render",
    "Niche": "Drama",
    "Language": "EN",
    "PromptHash": "d718125203c582da6a5e9c8d583b8bad",
    "EventID": "EN.Render.Drama.d718125203c582da6a5e9c8d583b8bad",
    "ParentEventID": "EN.Text.Drama.1de60ef338c2c6e4e88af012b82596d7",
    "PositionLayer": "",
    "RenderSequence": 0,
    "FinalRenderSequences": "[{\"EventID\":\"EN.Text.Drama.1de60ef338c2c6e4e88af012b82596d7\",\"MediaType\":\"Text\",\"PositionLayer\":\"HiddenScript\",\"RenderSequence\":-1,\"ContentLookupKey\":\"Text.77fad92d-4d17-469c-aa39-62c3c55138e8.a2f17833-8380-4d73-bcb6-c55be96741eb.json\"},{\"EventID\":\"EN.Image.Drama.e62048f67541d40470613616044680fe\",\"MediaType\":\"Image\",\"PositionLayer\":\"Thumbnail\",\"RenderSequence\":0,\"ContentLookupKey\":\"Image.77fad92d-4d17-469c-aa39-62c3c55138e8.5ab21af0-ac38-417a-9cbd-14f619d2129e.png\"},{\"EventID\":\"EN.Music.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Music\",\"PositionLayer\":\"BackgroundMusic\",\"RenderSequence\":0,\"ContentLookupKey\":\"m1.mp3\"},{\"EventID\":\"EN.Vocal.Drama.504b21a757e0ccd6aaa93fa20bc1af26\",\"MediaType\":\"Vocal\",\"PositionLayer\":\"Narrator\",\"RenderSequence\":0,\"ContentLookupKey\":\"Vocal.77fad92d-4d17-469c-aa39-62c3c55138e8.8627fe73-fe9d-4967-896b-a1fa08c82401.mp3\"},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"RenderSequence\":1,\"ContentLookupKey\":\"b30.mp4\"},{\"EventID\":\"EN.Vocal.Drama.9a785fadebd38db53593f5e42db636f2\",\"MediaType\":\"Vocal\",\"PositionLayer\":\"Narrator\",\"RenderSequence\":1,\"ContentLookupKey\":\"Vocal.77fad92d-4d17-469c-aa39-62c3c55138e8.fd3feb92-522e-4835-b100-b8403c4f4ad7.mp3\"},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"RenderSequence\":2,\"ContentLookupKey\":\"b17.mp4\"},{\"EventID\":\"EN.Vocal.Drama.ba0e372465a87f7c7ec1f2f2609ae9f9\",\"MediaType\":\"Vocal\",\"PositionLayer\":\"Narrator\",\"RenderSequence\":2,\"ContentLookupKey\":\"Vocal.77fad92d-4d17-469c-aa39-62c3c55138e8.6aebced5-3b6a-401c-b991-acc6bcdb1739.mp3\"},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"RenderSequence\":3,\"ContentLookupKey\":\"b29.mp4\"},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"RenderSequence\":4,\"ContentLookupKey\":\"b23.mp4\"},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"RenderSequence\":5,\"ContentLookupKey\":\"b18.mp4\"}]",
    "WatermarkText": "TrueVineMedia",
    "RestrictToPublisherID": "YoutubeProfile1",
    "MetaMediaDescriptor": "FinalRender"}
    mediaEvent = queue_wrapper.to_media_event(json.dumps(finalRenderEvent))

    renderer = video_render.VideoRender()

    return str(renderer.handle_final_render_video(mediaEvent=mediaEvent))