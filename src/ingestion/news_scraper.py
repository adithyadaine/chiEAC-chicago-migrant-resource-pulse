import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys
from datetime import datetime

# Add project root to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils import setup_logger, get_utc_timestamp

# Setup logger
logger = setup_logger('news_scraper', 'logs/news_scraper.log')

# Target URLs (Examples - strictly for educational/research purpose)
TARGET_URLS = [
    {"name": "Block Club Chicago", "url": "https://blockclubchicago.org/category/migrants/"},
    # Add more as discovered
]

def scrape_news():
    logger.info("Starting News Scraper...")
    all_articles = []

    for target in TARGET_URLS:
        try:
            logger.info(f"Scraping {target['name']}...")
            response = requests.get(target['url'], headers={'User-Agent': 'Mozilla/5.0 (Research Project)'})
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch {target['url']}: Status {response.status_code}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Note: Selector specificity will differ by site. This is a generic example.
            # Adjust selectors based on inspection of specific sites (Week 2 iteration).
            articles = soup.find_all('article')
            
            for art in articles[:10]: # Limit to 10 for testing
                headline_tag = art.find('h3') or art.find('h2')
                if headline_tag:
                    headline = headline_tag.get_text(strip=True)
                    link = headline_tag.find('a')['href'] if headline_tag.find('a') else "N/A"
                    
                    all_articles.append({
                        "source": target['name'],
                        "headline": headline,
                        "url": link,
                        "scraped_at": get_utc_timestamp()
                    })
                    
        except Exception as e:
            logger.error(f"Error scraping {target['name']}: {str(e)}")

    # Save to Bronze Layer
    if all_articles:
        df = pd.DataFrame(all_articles)
        filename = f"data/bronze/news/news_batch_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False)
        logger.info(f"Saved {len(all_articles)} articles to {filename}")
    else:
        logger.warning("No articles found.")

if __name__ == "__main__":
    scrape_news()
