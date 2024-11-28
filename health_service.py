import logging
import os
from flask import Flask

app = Flask(__name__)
logger = logging.getLogger(__name__)
@app.route("/health")
def health_check():
    return "Healthy"