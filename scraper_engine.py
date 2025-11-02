# 1. Import ALL our tools
import time
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# --- This is our "Master" confidence threshold ---
CONFIDENCE_THRESHOLD = 85 # Lowered a bit for real-world messy titles

# --- SCOUT 1: Our "Book Site" Scraper ---
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

# --- SCOUT 2: Our "Best Buy" Scraper ---
def scrape_best_buy(target_product_name):
    print(f"\n...[Scout 2: Checking Best Buy]...")
    
    search_term = requests.utils.quote(target_product_name)
    url = f"https://www.bestbuy.com/site/searchpage.jsp?st={search_term}"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Headless is ON
    chrome_options.add_argument("--log-level=3") 
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        print("  > Best Buy: Waiting 8 seconds for page to load...")
        time.sleep(8) 

        print(f"  > DEBUG: Page title is: {driver.title}")
        results = []
        products = driver.find_elements(By.CSS_SELECTOR, 'div.sku-block')
        print(f"  > DEBUG: Found {len(products)} product containers using 'div.sku-block'.")

        for product in products:
            try:
                title_element = product.find_element(By.CSS_SELECTOR, "h2.product-title")
                product_title = title_element.get_attribute('title')
                price_element = product.find_element(By.CSS_SELECTOR, 'div[data-testid="price-block-customer-price"]')
                price = price_element.text
                score = fuzz.token_sort_ratio(target_product_name, product_title)
                
                print(f"  > DEBUG: Checking '{product_title[0:50]}...' -- AI Score: {score}%")
                if score > CONFIDENCE_THRESHOLD:
                    print(f"  > +++ BEST BUY MATCH! (Score: {score}%) +++")
                    results.append({
                        "title": product_title,
                        "source": "bestbuy.com",
                        "price": price
                    })
            except Exception as e:
                print(f"  > DEBUG: Error in loop: {e}")
                continue 
        return results
    except Exception as e:
        print(f"  > ERROR: Best Buy scraper failed. {e}")
        return []
    finally:
        if driver:
            driver.quit()

# --- SCOUT 3: Our "Walmart" Scraper (The one that gets blocked) ---
def scrape_walmart(target_product_name):
    print(f"\n...[Scout 3: Checking Walmart]...")
    search_term = requests.utils.quote(target_product_name)
    url = f"https://www.walmart.com/search?q={search_term}"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Headless is ON
    chrome_options.add_argument("--log-level=3") 
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        print("  > Walmart: Waiting 8 seconds for page to load...")
        time.sleep(8)
        
        print(f"  > DEBUG: Page title is: {driver.title}")
        
        # We expect this to fail, but we're trying anyway
        if "Robot or human" in driver.title:
            print("  > DEBUG: Walmart blocked us with a CAPTCHA.")
            return []
            
        results = []
        products = driver.find_elements(By.CSS_SELECTOR, 'div[data-item-id]')
        print(f"  > DEBUG: Found {len(products)} product containers using 'div[data-item-id]'.")

        for product in products:
            try:
                title_element = product.find_element(By.CSS_SELECTOR, 'span[data-automation-id="product-title"]')
                product_title = title_element.text
                price_element = product.find_element(By.CSS_SELECTOR, 'div[data-automation-id="product-price"] > div')
                raw_price = price_element.text 
                
                if raw_price.startswith('$') and '.' not in raw_price:
                    price = f"{raw_price[:-2]}.{raw_price[-2:]}"
                else:
                    price = raw_price

                score = fuzz.token_sort_ratio(target_product_name, product_title)
                print(f"  > DEBUG: Checking '{product_title[0:50]}...' -- AI Score: {score}%")
                if score > CONFIDENCE_THRESHOLD:
                    print(f"  > +++ WALMART MATCH! (Score: {score}%) +++")
                    results.append({
                        "title": product_title,
                        "source": "walmart.com",
                        "price": price
                    })
            except Exception as e:
                print(f"  > DEBUG: Error in loop: {e}")
                continue 
        return results
    except Exception as e:
        print(f"  > ERROR: Walmart scraper failed. {e}")
        return []
    finally:
        if driver:
            driver.quit()

# --- SCOUT 4: Our NEW "Target" Scraper (You just found this!) ---
def scrape_target(target_product_name):
    print(f"\n...[Scout 4: Checking Target]...")
    
    search_term = requests.utils.quote(target_product_name)
    url = f"https://www.target.com/s?searchTerm={search_term}"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Headless is ON
    chrome_options.add_argument("--log-level=3") 
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        print("  > Target: Waiting 8 seconds for page to load...")
        time.sleep(8)

        print(f"  > DEBUG: Page title is: {driver.title}")
        
        if "are you a human" in driver.title.lower():
            print("  > DEBUG: Target blocked us with a CAPTCHA.")
            return []

        results = []
        
        # --- Using the "map" you found ---
        products = driver.find_elements(By.CSS_SELECTOR, 'div[data-test="product-details"]')
        print(f"  > DEBUG: Found {len(products)} product containers using 'div[data-test=\"product-details\"]'.")

        for product in products:
            try:
                title_element = product.find_element(By.CSS_SELECTOR, 'a[data-test="product-title"]')
                product_title = title_element.text
                
                price_element = product.find_element(By.CSS_SELECTOR, 'span[data-test="current-price"]')
                price = price_element.text

                score = fuzz.token_sort_ratio(target_product_name, product_title)
                print(f"  > DEBUG: Checking '{product_title[0:50]}...' -- AI Score: {score}%")

                if score > CONFIDENCE_THRESHOLD:
                    print(f"  > +++ TARGET MATCH! (Score: {score}%) +++")
                    results.append({
                        "title": product_title,
                        "source": "target.com",
                        "price": price
                    })
            except Exception as e:
                print(f"  > DEBUG: Error in loop: {e}")
                continue 

        return results
    except Exception as e:
        print(f"  > ERROR: Target scraper failed. {e}")
        return []
    finally:
        if driver:
            driver.quit()

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
    
    # --- NEW: Run scout 4 ---
    matches_4 = scrape_target(product_name)
    all_matches.extend(matches_4)
    
    print(f"--- DISPATCHER: Total matches found: {len(all_matches)} ---")
    return all_matches