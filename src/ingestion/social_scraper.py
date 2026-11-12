"""Community/nonprofit updates from free public feeds (Bluesky RSS + organisation blogs).
X/Twitter has no free access and Nitter is shut down, so it is no longer used."""
import os
import sys
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils import setup_logger, get_utc_timestamp
from src.ingestion.feeds import fetch_feed, is_relevant

logger = setup_logger('social_scraper', 'logs/social_scraper.log')

# (name, url, filter_by_keywords)
FEEDS = [
    ("Bluesky (@chicagohomeless)", "https://bsky.app/profile/chicagohomeless.bsky.social/rss", False),
    ("Bluesky (@fooddepository)", "https://bsky.app/profile/fooddepository.bsky.social/rss", False),
    ("Chicago Coalition for the Homeless", "https://chicagohomeless.org/feed/", False),
    ("Greater Chicago Food Depository", "https://www.chicagosfoodbank.org/feed/", False),
]

def scrape_social():
    logger.info("Starting community feed scraper...")
    rows, ok_feeds = [], 0
    for name, url, filt in FEEDS:
        try:
            items = fetch_feed(url)
            ok_feeds += 1
            for it in items:
                text = (it['title'] + ' ' + it['summary']).strip()
                if filt and not is_relevant(text):
                    continue
                rows.append({
                    "source": name,
                    "content": text[:1000],
                    "date": it['published'],
                    "scraped_at": get_utc_timestamp(),
                })
            logger.info(f"{name}: {len(items)} items")
        except Exception as e:
            logger.error(f"Error fetching {name} ({url}): {e}")

    if rows:
        df = pd.DataFrame(rows).drop_duplicates(subset=['source', 'content'])
        filename = f"data/bronze/social/community_batch_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False)
        logger.info(f"Saved {len(df)} posts to {filename} ({ok_feeds}/{len(FEEDS)} feeds ok)")
    else:
        logger.warning("No community posts found.")

if __name__ == "__main__":
    scrape_social()
