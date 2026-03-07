# Understanding Access Tokens and Refresh Tokens (Strava API)

Strava uses OAuth 2.0 for authentication. This involves two important
tokens:

------------------------------------------------------------------------

## Access Token

The access token is a temporary credential that allows your application
to:

-   Read your workout activities
-   Access distance, heart rate, and other fitness data
-   Call Strava API endpoints

### Important Characteristics:

-   Expires after a few hours (typically 6 hours)
-   Must be included in API request headers
-   Cannot be used after expiration

Example usage:

Authorization: Bearer ACCESS_TOKEN

------------------------------------------------------------------------

## Refresh Token

The refresh token is a long-lived credential that allows your
application to:

-   Request a new access token when the old one expires

It does NOT directly access Strava data.

### Important Characteristics:

-   Long-lived
-   Must be stored securely
-   Used to generate new access tokens

Example refresh request:

POST https://www.strava.com/oauth/token

With: - grant_type=refresh_token - client_id - client_secret -
refresh_token

Strava responds with: - new access_token - new refresh_token - new
expiration time

------------------------------------------------------------------------

## Why Two Tokens?

Security.

If an access token is compromised: - It expires quickly.

If a refresh token is compromised: - The attacker could generate new
access tokens. - Therefore, refresh tokens must be protected carefully.

------------------------------------------------------------------------

## Best Practice for Data Pipelines

For automated systems (e.g., Airflow):

1.  Store the refresh_token securely (Kubernetes Secret or Airflow
    Connection).
2.  Generate a new access_token at the start of each workflow run.
3.  Use the access_token to fetch activity data.
