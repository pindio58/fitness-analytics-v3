############################################
# Bootstrap script for first-time Strava auth
# Run once to populate tokens table
############################################

import requests
import psycopg2
from pathlib import Path

from settings import settings

# try:
#     from project_utils.logger import get_logger
# except ImportError:
#     from pathlib import Path as _Path

#     sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
#     from project_utils.logger import get_logger

from project_utils.logger import get_logger

logger = get_logger(__name__)


# -------------------------
# DB Connection (local)
# -------------------------
def get_connection():

    return psycopg2.connect(
        host=settings.pg_host,
        port=settings.pg_port,
        database=settings.pg_db,
        user=settings.pg_user,
        password=settings.pg_password,
    )


# -------------------------
# Exchange code for tokens
# -------------------------
def exchange_code_for_token(code):

    payload = {
        "client_id": settings.client_id,
        "client_secret": settings.client_secret,
        "code": code,
        "grant_type": "authorization_code",
    }

    response = requests.post(
        settings.AUTH_URL,
        data=payload,
    )

    response.raise_for_status()

    logger.info("Successfully received tokens from Strava")

    return response.json()


# -------------------------
# Insert tokens in DB
# -------------------------
def insert_tokens(data):

    athlete_id = data["athlete"]["id"]
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]
    expires_at = data["expires_at"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO fitness.strava_tokens
        (athlete_id, access_token, refresh_token, expires_at)
        VALUES (%s,%s,%s,%s)
        ON CONFLICT (athlete_id)
        DO UPDATE SET
            access_token=EXCLUDED.access_token,
            refresh_token=EXCLUDED.refresh_token,
            expires_at=EXCLUDED.expires_at;
        """,
        (athlete_id, access_token, refresh_token, expires_at),
    )

    conn.commit()

    cursor.close()
    conn.close()

    logger.info("Tokens stored successfully in database")


# -------------------------
# Script entry
# -------------------------
if __name__ == "__main__":

    print("\nOpen this URL in browser to authorize:\n")

    print(
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={settings.client_id}"
        f"&response_type=code"
        f"&redirect_uri=http://localhost/exchange_token"
        f"&approval_prompt=force"
        f"&scope=read,activity:read_all\n"
    )

    code = input("Paste the authorization code here: ")

    token_data = exchange_code_for_token(code)

    insert_tokens(token_data)

    logger.info("Bootstrap process completed successfully")
