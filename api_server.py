import os
from flask import Flask, jsonify, request, redirect, session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# --- We are importing our *disabled* scraper engine ---
from scraper_engine import run_all_scrapers

# === 1. SETUP THE FLASK APP ===
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# === 2. SETUP GOOGLE OAUTH ===
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
# This is your NEW, CORRECT Railway URL
REDIRECT_URI = 'https://price-agent-backend-production.up.railway.app/api/oauth/callback'
# This is the CORRECT, TYPO-FREE Google URL
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# --- NEW: A "Homepage" Test Route ---
@app.route("/")
def homepage_test():
    return "The BARE-MINIMUM Price Agent server is ALIVE!"

# --- This is our "Scraper" route (now disabled) ---
@app.route("/api/scrape")
def api_scrape_all():
    print("...Scraper is disabled...")
    return jsonify([])


# --- [NEW!] ROUTE 1: The "Login" Button ---
@app.route('/api/oauth/login')
def oauth_login():
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )
    session['state'] = state
    return redirect(authorization_url)


# --- [NEW!] ROUTE 2: The "Callback" Catcher ---
@app.route('/api/oauth/callback')
def oauth_callback():
    state = session['state']
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = REDIRECT_URI
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    print(f"--- NEW USER! ---")
    print(f"Refresh Token: {credentials.refresh_token}")
    return "<h1>Success!</h1><p>You have connected your Google Account. You can close this tab.</p>"

# --- This part runs the server ---
if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True, port=5000)
