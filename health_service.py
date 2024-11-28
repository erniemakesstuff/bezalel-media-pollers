import logging
import os
from flask import Flask
import clients.polly as polly

app = Flask(__name__)
logger = logging.getLogger(__name__)
@app.route("/health")
def health_check():
    polly.create_narration('testVocal.mp3', "Hello world", True)
    return "Healthy"