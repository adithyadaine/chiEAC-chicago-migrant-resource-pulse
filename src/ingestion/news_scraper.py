"""News ingestion from free public RSS feeds (replaces the old HTML scraper of one stale page)."""
import os
import sys
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils import setup_logger, get_utc_timestamp
from src.ingestion.feeds import fetch_feed, is_relevant

logger = setup_logger('news_scraper', 'logs/news_scraper.log')

GOOGLE = "https://news.google.com/rss/search?q={q}+when:7d&hl=en-US&gl=US&ceid=US:en"

# (name, url, filter_by_keywords)
FEEDS = [
    ("Block Club Chicago", "https://blockclubchicago.org/feed/", True),
    ("Chicago Sun-Times", "https://chicago.suntimes.com/rss/index.xml", True),
    ("WBEZ", "https://www.wbez.org/rss/index.xml", True),
    ("WTTW", "https://news.wttw.com/rss.xml", True),
    ("Google News", GOOGLE.format(q="Chicago+(migrants+OR+%22asylum+seekers%22+OR+newcomers)"), False),
    ("Google News", GOOGLE.format(q="Chicago+(shelter+OR+homelessness+OR+%22food+pantry%22)"), False),
]

def scrape_news():
    logger.info("Starting News Scraper (RSS)...")
    rows, ok_feeds = [], 0
    for name, url, filt in FEEDS:
        try:
            items = fetch_feed(url)
            ok_feeds += 1
            kept = 0
            for it in items:
                if filt and not is_relevant(it['title'] + ' ' + it['summary']):
                    continue
                if not it['link']:
                    continue
                rows.append({
                    "source": name,
                    "headline": it['title'],
                    "url": it['link'],
                    "published_at": it['published'],
                    "scraped_at": get_utc_timestamp(),
                })
                kept += 1
            logger.info(f"{name}: {len(items)} items, kept {kept} ({url[:60]})")
        except Exception as e:
            logger.error(f"Error fetching {name} ({url}): {e}")

    if rows:
        df = pd.DataFrame(rows).drop_duplicates(subset=['url'])
        filename = f"data/bronze/news/news_batch_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False)
        logger.info(f"Saved {len(df)} articles to {filename} ({ok_feeds}/{len(FEEDS)} feeds ok)")
    else:
        logger.warning("No articles found.")

if __name__ == "__main__":
    scrape_news()
