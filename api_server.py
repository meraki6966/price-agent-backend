from flask import Flask, jsonify, request
# We only import the ONE dispatcher function
from scraper_engine import run_all_scrapers

app = Flask(__name__)

@app.route("/api/scrape")
def api_scrape_all():
    print("...API request received...")
    
    # 1. Get the product name from the URL
    product_name = request.args.get('product')

    if not product_name:
        return jsonify({"error": "No product name provided."}), 400

    # 2. Run our "Dispatcher"
    # This ONE function now runs ALL our scouts
    matches = run_all_scrapers(product_name)
    
    print("...Scraping complete, sending all data back...")
    
    # 3. Return the final list of all matches
    return jsonify(matches)

# --- This part runs the server ---
if __name__ == "__main__":
    app.run(debug=True, port=5000)