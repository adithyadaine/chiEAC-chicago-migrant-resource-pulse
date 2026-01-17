import time
import os
import sys
import logging
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils import setup_logger, get_utc_timestamp

logger = setup_logger('social_scraper', 'logs/social_scraper.log')

# List of Nitter instances to try (Fallbacks)
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.bird.gardens",
    "https://nitter.moomoo.me",
    "https://nitter.cz" 
]

TARGET_HANDLES = ["@ChiHomeless", "@FoodDepository"]

def setup_driver():
    options = Options()
    # options.add_argument("--headless") # Disabled for debugging
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_social():
    logger.info("Starting Social Media Scraper (Multi-Instance Nitter)...")
    try:
        driver = setup_driver()
    except Exception as e:
        logger.error(f"Failed to initialize Chrome Driver: {e}. Ensure Chrome is installed and compatible.")
        return
    
    all_posts = []

    try:
        for handle in TARGET_HANDLES:
            success = False
            
            for instance in NITTER_INSTANCES:
                if success: break
                
                url = f"{instance}/search?f=tweets&q={handle}"
                logger.info(f"Trying {instance} for {handle}...")
                
                try:
                    driver.get(url)
                    
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC
                    
                    # Check for rate limit text specifically
                    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                    if "rate limited" in body_text or "no auth tokens" in body_text:
                        logger.warning(f"Rate limited on {instance}. Trying next...")
                        continue

                    # Wait for tweets
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "timeline-item"))
                    )
                    
                    # Use generic selector for Nitter
                    tweets = driver.find_elements(By.CLASS_NAME, "timeline-item")
                    
                    if not tweets:
                        logger.warning(f"No tweets found on {instance} (structure might vary).")
                        continue
                        
                    logger.info(f"Success! Found {len(tweets)} tweets on {instance}")
                    
                    for tweet in tweets[:15]:
                        try:
                            content = tweet.find_element(By.CLASS_NAME, "tweet-content").text
                            # Date is often in a title attribute
                            try:
                                date_el = tweet.find_element(By.CLASS_NAME, "tweet-date").find_element(By.TAG_NAME, 'a')
                                date_str = date_el.get_attribute('title')
                            except:
                                date_str = datetime.now().strftime("%Y-%m-%d")

                            all_posts.append({
                                "source": f"Nitter ({handle})",
                                "content": content,
                                "date": date_str,
                                "scraped_at": get_utc_timestamp()
                            })
                        except:
                            continue
                            
                    success = True

                except Exception as e:
                    logger.warning(f"Failed on {instance}: {str(e)}")
            
            if not success:
                logger.error(f"Could not scrape {handle} from any instance.")

    except Exception as e:
        logger.error(f"Fatal scraper error: {e}")
    finally:
        driver.quit()

    # Save Results
    if all_posts:
        filename = f"data/bronze/social/nitter_batch_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        pd.DataFrame(all_posts).to_csv(filename, index=False)
        logger.info(f"Saved {len(all_posts)} tweets to {filename}")
    else:
        logger.warning("No tweets extracted from any source.")

if __name__ == "__main__":
    scrape_social()
