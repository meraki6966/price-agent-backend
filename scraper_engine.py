# 1. Import our (now limited) tools
import time
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
# We have "commented out" all selenium imports
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options

# --- This is our "Master" confidence threshold ---
CONFIDENCE_THRESHOLD = 85 

# --- SCOUT 1: Our "Book Site" Scraper (This one WILL work!) ---
def scrape_book_catalog(target_product_name):
    print(f"\n...[Scout 1: Checking Book Site]...")
    url = "http://books.toscrape.com/catalogue/category/books_1/index.html"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'} 
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        books = soup.find_all('article', class_='product_pod')
        results = [] 

        for book in books:
            try:
                book_title = book.find('h3').find('a')['title']
                price = book.find('p', class_='price_color').get_text()
                score = fuzz.ratio(target_product_name, book_title)

                if score > CONFIDENCE_THRESHOLD:
                    print(f"  > BOOK MATCH! (Score: {score}%)")
                    results.append({
                        "title": book_title,
                        "source": "books.toscrape.com",
                        "price": price
                    })
            except:
                continue 
        return results

    except Exception as e:
        print(f"  > ERROR: Book site scraper failed. {e}")
        return []

# --- SCOUT 2: "Best Buy" (Disabled) ---
def scrape_best_buy(target_product_name):
    print(f"\n...[Scout 2: Best Buy - DISABLED FOR DEPLOYMENT]...")
    return [] # Just return an empty list

# --- SCOUT 3: "Walmart" (Disabled) ---
def scrape_walmart(target_product_name):
    print(f"\n...[Scout 3: Walmart - DISABLED FOR DEPLOYMENT]...")
    return [] # Just return an empty list

# --- SCOUT 4: "Target" (Disabled) ---
def scrape_target(target_product_name):
    print(f"\n...[Scout 4: Target - DISABLED FOR DEPLOYMENT]...")
    return [] # Just return an empty list


# --- THE DISPATCHER: This runs ALL our scouts ---
def run_all_scrapers(product_name):
    print(f"\n--- DISPATCHER: Searching for '{product_name}' ---")
    
    all_matches = [] # A master list
    
    matches_1 = scrape_book_catalog(product_name)
    all_matches.extend(matches_1)
    
    matches_2 = scrape_best_buy(product_name)
    all_matches.extend(matches_2)

    matches_3 = scrape_walmart(product_name)
    all_matches.extend(matches_3)
    
    matches_4 = scrape_target(product_name)
    all_matches.extend(matches_4)
    
    print(f"--- DISPATCHER: Total matches found: {len(all_matches)} ---")
    return all_matches
