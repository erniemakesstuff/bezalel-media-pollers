import json
import logging
import os
from flask import Flask, request
from clients.rate_limiter import RateLimiter
import queue_wrapper
from callbacks.renderers import video_render
from callbacks import image_callback
app = Flask(__name__)
logger = logging.getLogger(__name__)
@app.route("/health")
def health_check():
    return "Healthy"

@app.route("/ratelimit", methods=['POST'])
def rate_limiter():
    data = request.get_json()
    api_name = data.get('apiName')
    max_requests = data.get('maxRequestsPerMin')
    if api_name == None or len(api_name) == 0:
        return "empty api name", 400
    if max_requests == None or max_requests <= 0:
        return "invalid max requests", 400
    
    is_allowed = RateLimiter().is_allowed(api_name=api_name, max_requests_minute=max_requests)
    if is_allowed:
        return api_name + " allowed", 200
    else:
        return api_name + " rate limited", 429

@app.route("/test")
def testRender():
    finalRenderEvent = {
        "LedgerID": "fb6d74ee-401e-4c68-918b-bb6c93c3219d",
        "PromptInstruction": "OriginalPromptHash: d015e40609311da0195356a5d856a027 - MetaDescriptor: FinalRender - OPT_PUB: YouTubeTest",
        "SystemPromptInstruction": "OriginalPromptHash: d015e40609311da0195356a5d856a027 - MetaDescriptor: FinalRender - OPT_PUB: YouTubeTest",
        "MediaType": "Render",
        "DistributionFormat": "ShortVideo",
        "ContentLookupKey": "Render.fb6d74ee-401e-4c68-918b-bb6c93c3219d.31695401-ee99-419e-963a-3cd245b6df58.render",
        "Niche": "Drama",
        "Language": "EN",
        "PromptHash": "6a214b0c4c620716b739d1352f817bc3",
        "EventID": "EN.Render.Drama.6a214b0c4c620716b739d1352f817bc3",
        "ParentEventID": "EN.Text.Drama.d015e40609311da0195356a5d856a027",
        "PositionLayer": "",
        "RenderSequence": 0,
        "FinalRenderSequences": "[{\"EventID\":\"EN.Text.Drama.d015e40609311da0195356a5d856a027\",\"MediaType\":\"Text\",\"PositionLayer\":\"HiddenScript\",\"ContentLookupKey\":\"Text.fb6d74ee-401e-4c68-918b-bb6c93c3219d.a014c850-25d1-4be6-8e0e-f003863064b9.json\",\"RenderSequence\":-1},{\"EventID\":\"EN.Image.Drama.752a25f1009c5d6f2156ad10d4efb912\",\"MediaType\":\"Image\",\"PositionLayer\":\"Thumbnail\",\"ContentLookupKey\":\"Image.fb6d74ee-401e-4c68-918b-bb6c93c3219d.9794d2af-80fd-4ba3-9d64-f48d1fbdbe53.png\",\"RenderSequence\":0},{\"EventID\":\"EN.Music.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Music\",\"PositionLayer\":\"BackgroundMusic\",\"ContentLookupKey\":\"m6.mp3\",\"RenderSequence\":0},{\"EventID\":\"EN.Vocal.Drama.b295e24d0735919c32bec1e1469517b9\",\"MediaType\":\"Vocal\",\"PositionLayer\":\"Narrator\",\"ContentLookupKey\":\"Vocal.fb6d74ee-401e-4c68-918b-bb6c93c3219d.38579ddf-b5d6-45c6-9945-872813308f94.mp3\",\"RenderSequence\":0},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"ContentLookupKey\":\"b9.mp4\",\"RenderSequence\":1},{\"EventID\":\"EN.Vocal.Drama.b085f4aa84e842fa04987b26b6101c2a\",\"MediaType\":\"Vocal\",\"PositionLayer\":\"Narrator\",\"ContentLookupKey\":\"Vocal.fb6d74ee-401e-4c68-918b-bb6c93c3219d.ef525c6d-59f2-4e58-97c2-4a23f4a94e55.mp3\",\"RenderSequence\":1},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"ContentLookupKey\":\"b64.mp4\",\"RenderSequence\":2},{\"EventID\":\"EN.Vocal.Drama.ff1ed6f6d15d9ec5d5b9f81096230a75\",\"MediaType\":\"Vocal\",\"PositionLayer\":\"Narrator\",\"ContentLookupKey\":\"Vocal.fb6d74ee-401e-4c68-918b-bb6c93c3219d.3f10d329-d719-415f-ae5b-857a73d37906.mp3\",\"RenderSequence\":2},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"ContentLookupKey\":\"b11.mp4\",\"RenderSequence\":3},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"ContentLookupKey\":\"b68.mp4\",\"RenderSequence\":4},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"ContentLookupKey\":\"b38.mp4\",\"RenderSequence\":5}]",
        "WatermarkText": "Kherem.com",
        "RestrictToPublisherID": "YouTubeTest",
        "MetaMediaDescriptor": "FinalRender"
    }
    mediaEvent = queue_wrapper.to_media_event(json.dumps(finalRenderEvent))

    renderer = video_render.VideoRender()
    logger.info("calling video render")
    return str(renderer.handle_final_render_video(mediaEvent=mediaEvent))

@app.route("/test-image")
def testImage():
    finalRenderEvent = {
        "LedgerID": "fb6d74ee-401e-4c68-918b-bb6c93c3219d",
        "PromptInstruction": "A happy cat",
        "SystemPromptInstruction": "OriginalPromptHash: d015e40609311da0195356a5d856a027 - MetaDescriptor: FinalRender - OPT_PUB: YouTubeTest",
        "MediaType": "Image",
        "DistributionFormat": "ShortVideo",
        "ContentLookupKey": "test_image_watermark.png",
        "Niche": "Drama",
        "Language": "EN",
        "PromptHash": "6a214b0c4c620716b739d1352f817bc3",
        "EventID": "EN.Render.Drama.6a214b0c4c620716b739d1352f817bc3",
        "ParentEventID": "EN.Text.Drama.d015e40609311da0195356a5d856a027",
        "PositionLayer": "",
        "RenderSequence": 0,
        "FinalRenderSequences": "[{\"EventID\":\"EN.Text.Drama.d015e40609311da0195356a5d856a027\",\"MediaType\":\"Text\",\"PositionLayer\":\"HiddenScript\",\"ContentLookupKey\":\"Text.fb6d74ee-401e-4c68-918b-bb6c93c3219d.a014c850-25d1-4be6-8e0e-f003863064b9.json\",\"RenderSequence\":-1},{\"EventID\":\"EN.Image.Drama.752a25f1009c5d6f2156ad10d4efb912\",\"MediaType\":\"Image\",\"PositionLayer\":\"Thumbnail\",\"ContentLookupKey\":\"Image.fb6d74ee-401e-4c68-918b-bb6c93c3219d.9794d2af-80fd-4ba3-9d64-f48d1fbdbe53.png\",\"RenderSequence\":0},{\"EventID\":\"EN.Music.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Music\",\"PositionLayer\":\"BackgroundMusic\",\"ContentLookupKey\":\"m6.mp3\",\"RenderSequence\":0},{\"EventID\":\"EN.Vocal.Drama.b295e24d0735919c32bec1e1469517b9\",\"MediaType\":\"Vocal\",\"PositionLayer\":\"Narrator\",\"ContentLookupKey\":\"Vocal.fb6d74ee-401e-4c68-918b-bb6c93c3219d.38579ddf-b5d6-45c6-9945-872813308f94.mp3\",\"RenderSequence\":0},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"ContentLookupKey\":\"b9.mp4\",\"RenderSequence\":1},{\"EventID\":\"EN.Vocal.Drama.b085f4aa84e842fa04987b26b6101c2a\",\"MediaType\":\"Vocal\",\"PositionLayer\":\"Narrator\",\"ContentLookupKey\":\"Vocal.fb6d74ee-401e-4c68-918b-bb6c93c3219d.ef525c6d-59f2-4e58-97c2-4a23f4a94e55.mp3\",\"RenderSequence\":1},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"ContentLookupKey\":\"b64.mp4\",\"RenderSequence\":2},{\"EventID\":\"EN.Vocal.Drama.ff1ed6f6d15d9ec5d5b9f81096230a75\",\"MediaType\":\"Vocal\",\"PositionLayer\":\"Narrator\",\"ContentLookupKey\":\"Vocal.fb6d74ee-401e-4c68-918b-bb6c93c3219d.3f10d329-d719-415f-ae5b-857a73d37906.mp3\",\"RenderSequence\":2},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"ContentLookupKey\":\"b11.mp4\",\"RenderSequence\":3},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"ContentLookupKey\":\"b68.mp4\",\"RenderSequence\":4},{\"EventID\":\"EN.Video.Drama.d51dd44aed31246786008ac979766cbe\",\"MediaType\":\"Video\",\"PositionLayer\":\"Fullscreen\",\"ContentLookupKey\":\"b38.mp4\",\"RenderSequence\":5}]",
        "WatermarkText": "Kherem.com",
        "RestrictToPublisherID": "YouTubeTest",
        "MetaMediaDescriptor": "FinalRender"
    }
    mediaEvent = queue_wrapper.to_media_event(json.dumps(finalRenderEvent))

    renderer = image_callback.ImageCallbackHandler()
    logger.info("calling get image")
    return str(renderer.handle_image_generation(mediaEvent=mediaEvent))