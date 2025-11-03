# === V4 - Super-Clean Deploy ===
import os
from flask import Flask, jsonify, request, redirect, session
... (rest of the code)
import os
from flask import Flask, jsonify, request, redirect, session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# --- Our Imports from Phase 1 ---
from scraper_engine import run_all_scrapers

# === 1. SETUP THE FLASK APP ===
app = Flask(__name__)
# We get this from Render's Environment Variables
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# === 2. SETUP GOOGLE OAUTH ===
# We get these from Render's Environment Variables
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = 'https://price-agent-backend-production.up.railway.app/api/oauth/callback'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# --- NEW: A "Homepage" Test Route ---
@app.route("/")
def homepage_test():
    # This is a test route to make sure the server is alive
    return "The NEW Price Agent server is ALIVE! (v3 - TYPO FIXED)"

# --- This is our "Scraper" route (from Phase 1) ---
@app.route("/api/scrape")
def api_scrape_all():
    print("...API request received...")
    product_name = request.args.get('product')
    if not product_name:
        return jsonify({"error": "No product name provided."}), 400
    
    matches = run_all_scrapers(product_name)
    print("...Scraping complete, sending all data back...")
    return jsonify(matches)


# --- [NEW!] ROUTE 1: The "Login" Button ---
@app.route('/api/oauth/login')
def oauth_login():
    # 1. Create a "flow" object using our Client ID and Secret
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

    # 2. Generate the special Google "permission" URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )
    
    # 3. Save the "state" in the user's session
    session['state'] = state

    # 4. Send the user to the Google "permission" page
    return redirect(authorization_url)


# --- [NEW!] ROUTE 2: The "Callback" Catcher ---
@app.route('/api/oauth/callback')
def oauth_callback():
    # 1. Check the "state" to make sure it's the same user
    state = session['state']
    
    # 2. Create the "flow" object again
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

    # 3. Get the "authorization code" that Google put in the URL
    authorization_response = request.url
    
    # 4. "Fetch" the real, permanent tokens from Google
    flow.fetch_token(authorization_response=authorization_response)

    # 5. Get the user's permanent "Refresh Token"
    credentials = flow.credentials
    print(f"--- NEW USER! ---")
    print(f"Refresh Token: {credentials.refresh_token}")
    
    # We would save this token to a database
    
    # 6. Send the user to a "Success!" page
    return "<h1>Success!</h1><p>You have connected your Google Account. You can close this tab.</p>"

# --- This part runs the server ---
if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True, port=5000)



