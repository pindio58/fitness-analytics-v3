# Strava API Complete Setup Guide

This document explains the complete end-to-end process for connecting to
the Strava API, generating tokens, and testing endpoints using Bruno.

------------------------------------------------------------------------

# 1️⃣ Create a Strava Developer App

1.  Go to: https://www.strava.com/settings/api
2.  Click **Create & Manage Your App**
3.  Fill in:
    -   Application Name
    -   Category: Other
    -   Website: http://localhost
    -   Authorization Callback Domain: localhost
4.  Upload any icon image
5.  Save

You will receive: - Client ID - Client Secret

------------------------------------------------------------------------

# 2️⃣ Authorize Your Athlete Account

Open this URL in your browser (replace CLIENT_ID):

https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all

After approving access, you will be redirected to:

http://localhost/?state=&code=AUTHORIZATION_CODE

Copy the value of `code` from the URL.

------------------------------------------------------------------------

# 3️⃣ Exchange Code for Access Token

In Bruno (or Postman):

POST\
https://www.strava.com/oauth/token

Body → Form URL Encoded:

-   client_id = YOUR_CLIENT_ID
-   client_secret = YOUR_CLIENT_SECRET
-   code = AUTHORIZATION_CODE
-   grant_type = authorization_code

Response will include:

-   access_token
-   refresh_token
-   expires_at
-   athlete object

Save the access_token and refresh_token.

------------------------------------------------------------------------

# 4️⃣ Call Strava API

Example:

GET\
https://www.strava.com/api/v3/athlete

Headers:

Authorization: Bearer YOUR_ACCESS_TOKEN

If successful, you will receive athlete JSON data.

------------------------------------------------------------------------

# 5️⃣ Understanding Token Expiry

-   expires_in = 21600 seconds (6 hours)
-   expires_at = Unix timestamp of expiration

Access tokens expire after 6 hours.

------------------------------------------------------------------------

# 6️⃣ Refresh Expired Token

When access token expires:

POST\
https://www.strava.com/oauth/token

Body → Form URL Encoded:

-   client_id = YOUR_CLIENT_ID
-   client_secret = YOUR_CLIENT_SECRET
-   grant_type = refresh_token
-   refresh_token = YOUR_REFRESH_TOKEN

Response returns:

-   NEW access_token
-   NEW refresh_token
-   NEW expires_at

Important: Always save the new refresh_token.

------------------------------------------------------------------------

# 7️⃣ Recommended Testing Flow

1.  Test /athlete endpoint first
2.  Then test: GET /api/v3/athlete/activities?per_page=200
3.  Inspect JSON structure
4.  Plan database schema
5.  Automate refresh logic in Airflow or backend

------------------------------------------------------------------------

# 8️⃣ Common Errors

Authorization Error: - Missing "Bearer" prefix - Expired token - Using
refresh_token instead of access_token - Environment variable not
resolving - Redirect URI mismatch

------------------------------------------------------------------------

You now have a complete working Strava API authentication and testing
workflow.
