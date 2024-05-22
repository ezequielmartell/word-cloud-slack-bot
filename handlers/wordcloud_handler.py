from datetime import datetime
from collections import Counter
from utils.wordcloud import create_word_cloud, create_word_cloud_from_dict
from utils.slack_client import app
import requests

@app.command("/wordcloud")
def handle_slash_command(ack, body, context):
    ack()
    bot_token = context['token']
    text = body.get('text')
    current_time = datetime.now()
    time_stamp = current_time.timestamp()
    channel = context['channel_id']

    if text == "usernames":
        handle_usernames(bot_token, channel, time_stamp)
    else:
        handle_messages(bot_token, channel, time_stamp)

def handle_usernames(bot_token, channel, time_stamp):
    messages = get_channel_messages(bot_token, channel)
    cloud_users = [msg.get('user') for msg in messages if msg.get('type') == "message" and not msg.get('subtype')]

    usernames = get_usernames_from_ids(cloud_users, bot_token)
    word_cloud_dict = Counter(usernames)
    wordcloud = create_word_cloud_from_dict(word_cloud_dict)

    upload_wordcloud(wordcloud, bot_token, channel, time_stamp)

def handle_messages(bot_token, channel, time_stamp):
    messages = get_channel_messages(bot_token, channel)
    cloud_text = ' '.join([msg.get('text') for msg in messages if msg.get('type') == "message"])

    wordcloud = create_word_cloud(cloud_text)
    upload_wordcloud(wordcloud, bot_token, channel, time_stamp)

def get_channel_messages(bot_token, channel):
    result = app.client.conversations_history(token=bot_token, channel=channel, limit=100)
    return result['messages']

def get_usernames_from_ids(user_ids, bot_token):
    usernames = []
    cache = {}
    for user_id in user_ids:
        if user_id not in cache:
            user_info = app.client.users_info(token=bot_token, user=user_id)
            display_name = user_info['user']['profile']['display_name'] or user_info['user']['profile']['real_name']
            cache[user_id] = display_name
        usernames.append(cache[user_id])
    return usernames

def upload_wordcloud(wordcloud, bot_token, channel, time_stamp):
    external_upload = app.client.files_getUploadURLExternal(
        token=bot_token,
        filename=f"wordcloud-{time_stamp}.png",
        length=len(wordcloud.getvalue())
    )
    requests.post(external_upload['upload_url'], data=wordcloud)
    app.client.files_completeUploadExternal(
        token=bot_token,
        channel_id=channel,
        files=[{"id": external_upload['file_id']}],
        initial_comment=""
    )
