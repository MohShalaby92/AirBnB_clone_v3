#!/usr/bin/python3
"""Endpoint (route) will be to return the status of your API"""
import os
from os import getenv
from flask import Flask
from models import storage
from api.v1.views import app_views
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "0.0.0.0"}})

app.register_blueprint(app_views, url_prefix="/api/v1")

@app.errorhandler(404)
def page_not_found(e):
    return {"error": "Not found"}, 404

app.teardown_appcontext
def teardown_session(exception):
    storage.close()


if __name__ == "__main__":
    HBNB_API_HOST = getenv("HBNB_API_HOST")
    HBNB_API_PORT = getenv("HBNB_API_PORT")

    host = "0.0.0.0" if not HBNB_API_HOST else HBNB_API_HOST
    port = 5000 if not HBNB_API_PORT else HBNB_API_PORT
    app.run(host=host, port=port, threaded=True)
