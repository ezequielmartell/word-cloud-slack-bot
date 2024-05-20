import os
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore
from slack_bolt import App
from dotenv import load_dotenv
import requests
from io import BytesIO
from wordcloud import WordCloud
import datetime
from collections import Counter

load_dotenv()

user_auth_url = "https://finer-yak-visually.ngrok-free.app/slack/install"

oauth_settings = OAuthSettings(
    client_id=os.environ["SLACK_CLIENT_ID"],
    client_secret=os.environ["SLACK_CLIENT_SECRET"],
    scopes=["commands"],  # "channels:history", "files:write"],
    user_scopes=["chat:write", "files:write", "channels:history", "users:read"],
    installation_store=FileInstallationStore(base_dir="./data/installations"),
    state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data/states")
)

app = App(
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    oauth_settings=oauth_settings
)


def create_word_cloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    img_buffer = BytesIO()
    wordcloud.to_image().save(img_buffer, format='PNG')
    img_buffer.seek(0)  # Rewind the buffer to the beginning
    return img_buffer


@app.command("/wordcloud")
def handle_slash_command(ack, body, say, context, respond):
    # Acknowledge command request
    ack()
    bot_token = context['token']
    text = body.get('text')
    current_time = datetime.datetime.now()
    time_stamp = current_time.timestamp()
    print(context)

    if text == "usernames":
        # print(context)
        channel = context['channel_id']

        messages = app.client.conversations_history(
            token=bot_token,
            # token=bot_token,
            channel=channel,
            limit=100
        )
        messages = messages['messages']
        # print(messages)
        cloud_users = []
        for message in messages:
            if message.get('type') == "message" and not (message.get('subtype')):
                cloud_users.append(message.get('user'))

        usernames = []
        cache = {}
        # print(cloud_users)
        for userid in cloud_users:
            user = cache.get(userid)
            if user is None:
                print(f"userid: {userid}")
                user = app.client.users_info(
                    token=bot_token,
                    user=userid
                )
                display_name = user['user']['profile']['display_name']
                # print(user['user']['profile'])
                if display_name == '':
                    display_name = user['user']['profile']['real_name']
                usernames.append(display_name)
                cache[userid] = display_name
            else:
                usernames.append(user)

        print(usernames)
        word_cloud_dict = Counter(usernames)
        # word_cloud = create_word_cloud(word_cloud_dict)
        wordcloud = WordCloud(width=800, height=400,
                              background_color='white').generate_from_frequencies(word_cloud_dict)

        # Create a BytesIO object and save the word cloud to it
        img_buffer = BytesIO()
        wordcloud.to_image().save(img_buffer, format='PNG')
        img_buffer.seek(0)

        external_upload = app.client.files_getUploadURLExternal(
            token=bot_token,
            # token=bot_token,
            filename=f"wordcloud-{time_stamp}.png",
            length=len(img_buffer.getvalue())
        )
        response = requests.post(external_upload['upload_url'], data=img_buffer)

        app.client.files_completeUploadExternal(
            # token=bot_token,
            token=bot_token,
            channel_id=channel,
            files=[{"id": external_upload['file_id']}],
            initial_comment=""
        )

    else:
        # print(context)
        channel = context['channel_id']

        messages = app.client.conversations_history(
            token=bot_token,
            # token=bot_token,
            channel=channel,
            limit=100
        )
        messages = messages['messages']
        print(messages)
        cloud_text = ''
        for message in messages:
            if message.get('type') == "message":
                cloud_text += " " + message.get('text')

        word_cloud = create_word_cloud(cloud_text)

        external_upload = app.client.files_getUploadURLExternal(
            token=bot_token,
            # token=bot_token,
            filename=f"wordcloud-{time_stamp}.png",
            length=len(word_cloud.getvalue())
        )
        response = requests.post(external_upload['upload_url'], data=word_cloud)

        app.client.files_completeUploadExternal(
            # token=bot_token,
            token=bot_token,
            channel_id=channel,
            files=[{"id": external_upload['file_id']}],
            initial_comment=""
        )


# Ready? Start your app!
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
