############################################
## Handles:                               ##
##    reading tokens from Postgres        ##
##    refreshing them if expired          ##
##    returning a valid access token      ##
############################################

import psycopg2
import requests
import logging
import os
from datetime import datetime, timezone, timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook

from strava_module.settings import settings

# -------------------------
# Logging configuration
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("strava_token_manager")

athlete_id=os.getenv('athelete_id')

# -------------------------
# DB Connection
# -------------------------
def get_connection():
    try:
        logger.info("Opening database connection")

        # conn = psycopg2.connect(
        #     database="postgresdb",
        #     user="postgresadmin",
        #     password="admin123",
        #     host="fitness-analytics-postgres-service",
        #     port="5432",
        # )
        hook = PostgresHook(postgres_conn_id=settings.AIRFLOW_CONN_POSTGRES)
        conn = hook.get_conn()
        logger.info("Database connection established")
        return conn

    except Exception:
        logger.exception("Failed to connect to database")
        raise


# -------------------------
# Read token from DB
# -------------------------
def get_token(athlete_id):
    logger.info(f"Fetching token for athlete_id={athlete_id}")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT access_token, refresh_token, expires_at
            FROM fitness.strava_tokens
            WHERE athlete_id=%s;
            """,
            (athlete_id,),
        )

        row = cursor.fetchone()

        if not row:
            logger.error("No token found in database")
            raise ValueError("Token not found")

        access_token, refresh_token, expires_at = row

        logger.info("Token successfully retrieved from database")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
        }

    except Exception:
        logger.exception("Error while retrieving token")
        raise

    finally:
        if "conn" in locals():
            cursor.close()
            conn.close()
            logger.info("Database connection closed")


# -------------------------
# Refresh token via Strava
# -------------------------
def refresh_token(refresh_token):
    logger.info("Refreshing Strava access token")

    payload = {
        "client_id": settings.client_id,
        "client_secret": settings.client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    try:
        # logger.info(payload)
        response = requests.post(url=settings.AUTH_URL, data=payload)

        logger.info(f"Strava API response status: {response.status_code}")

        response.raise_for_status()

        logger.info("Token refresh successful")

        return response.json()

    except requests.RequestException:
        logger.exception("Token refresh failed")
        raise


# -------------------------
# Update DB tokens
# -------------------------
def update_tokens(athlete_id, access_token, refresh_token, expires_at):
    logger.info(f"Updating tokens in DB for athlete_id={athlete_id}")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE fitness.strava_tokens
            SET
                access_token=%s,
                refresh_token=%s,
                expires_at=%s,
                updated_at=CURRENT_TIMESTAMP
            WHERE athlete_id=%s;
            """,
            (access_token, refresh_token, expires_at, athlete_id),
        )

        conn.commit()

        logger.info("Tokens successfully updated in database")

    except Exception:
        logger.exception("Failed to update tokens in database")
        raise

    finally:
        if "conn" in locals():
            cursor.close()
            conn.close()
            logger.info("Database connection closed")


# -------------------------
# Main token manager
# -------------------------
def get_valid_token(athlete_id):

    logger.info("Checking token validity")

    token = get_token(athlete_id=athlete_id)

    now = datetime.now(timezone.utc)
    expires_at = datetime.fromtimestamp(token["expires_at"], timezone.utc)

    logger.info(f"Token expires at: {expires_at}")

    if now >= expires_at - timedelta(minutes=5):

        logger.info("Token is expired or about to expire. Refreshing...")

        new_token = refresh_token(token["refresh_token"])

        update_tokens(
            athlete_id=athlete_id,
            access_token=new_token["access_token"],
            refresh_token=new_token["refresh_token"],
            expires_at=new_token["expires_at"],
        )

        logger.info("Returning refreshed access token")

        return new_token["access_token"]

    logger.info("Existing token still valid")

    return token["access_token"]


# -------------------------
# Script entry
# -------------------------
if __name__ == "__main__":

    logger.info("Starting Strava token manager script")

    token = get_valid_token(settings.athlete_id)

    logger.info("Successfully obtained valid access token")