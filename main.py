import os
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from utils.slack_client import app
import handlers.wordcloud_handler
from dotenv import load_dotenv

load_dotenv()
PORT = os.environ["PORT"]

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@flask_app.route("/slack/install", methods=["GET"])
def install():
    return handler.handle(request)

@flask_app.route("/slack/oauth_redirect", methods=["GET"])
def oauth_redirect():
    return handler.handle(request)

if __name__ == "__main__":
    flask_app.run(port=PORT)
