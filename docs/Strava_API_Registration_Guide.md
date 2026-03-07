# How to Register for the Strava API

This guide explains how to register your application with Strava and
obtain the required credentials.

## Step 1: Create a Strava Account

If you do not already have an account, create one at:
https://www.strava.com

------------------------------------------------------------------------

## Step 2: Go to Strava Developer Settings

Visit: https://www.strava.com/settings/api

Click **Create & Manage Your App**.

------------------------------------------------------------------------

## Step 3: Create a New Application

Fill in the following details:

-   **Application Name**: (e.g., Fitness Analytics)
-   **Category**: Performance
-   **Website**: <https://github.com>(for personal projects)
-   **Authorization Callback Domain**: localhost
-   **Icon**: Upload any simple PNG image

Click **Create**.

------------------------------------------------------------------------

## Step 4: Save Your Credentials

After creating the app, you will receive:

-   Client ID
-   Client Secret
-   Refresh token

Store these securely. You will need them to authenticate with the Strava
API.

------------------------------------------------------------------------

## Step 5: Authorize Your Application

Open the following URL in your browser (replace YOUR_CLIENT_ID):

https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all

After approval, you will receive an authorization code.

------------------------------------------------------------------------

## Step 6: Exchange Code for Tokens

Send a POST request to:

https://www.strava.com/oauth/token

With: - client_id - client_secret - code - grant_type=authorization_code

You will receive: - access_token - refresh_token - expires_at

Store the refresh_token securely.
