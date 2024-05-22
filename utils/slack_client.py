import os
from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store.sqlalchemy import SQLAlchemyInstallationStore
from slack_sdk.oauth.state_store.sqlalchemy import SQLAlchemyOAuthStateStore
import sqlalchemy
from sqlalchemy.engine import Engine
from dotenv import load_dotenv


load_dotenv()

bot_base_url = os.environ["BOT_BASE_URL"]
user_auth_url = f"https://{bot_base_url}/slack/install"

db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASSWORD"]
database_url = f"postgresql://{db_user}:{db_pass}@word-cloud-db/slackapp"

bot_scopes = ["commands", "channels:history", "files:write", "users:read"]
client_id, client_secret, signing_secret = (
    os.environ["SLACK_CLIENT_ID"],
    os.environ["SLACK_CLIENT_SECRET"],
    os.environ["SLACK_SIGNING_SECRET"],
)

engine: Engine = sqlalchemy.create_engine(database_url)
installation_store = SQLAlchemyInstallationStore(
    client_id=client_id,
    engine=engine,
)
oauth_state_store = SQLAlchemyOAuthStateStore(
    expiration_seconds=120,
    engine=engine,
)

try:
    engine.connect("select count(*) from slack_bots")
except Exception as e:
    installation_store.metadata.create_all(engine)
    oauth_state_store.metadata.create_all(engine)

app = App(
    signing_secret=signing_secret,
    installation_store=installation_store,
    oauth_settings=OAuthSettings(
        scopes=bot_scopes,
        client_id=client_id,
        client_secret=client_secret,
        state_store=oauth_state_store,
    ),
)