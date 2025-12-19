import pandas as pd
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils import setup_logger, get_utc_timestamp

logger = setup_logger('gov_ingest', 'logs/gov_ingest.log')

# Datasets:
# 1. New Arrivals Vendor Payments (Resource Spend) - ID: gxzc-43gg
# 2. Emergency Temporary Shelters Census (Headcounts) - ID: a4p3-hxgg
DATASETS = {
    "vendor_payments": "https://data.cityofchicago.org/resource/gxzc-43gg.json",
    "shelter_census": "https://data.cityofchicago.org/resource/a4p3-hxgg.json"
}

def ingest_gov_data():
    logger.info("Starting Government Data Ingestion...")
    try:
        for name, url in DATASETS.items():
            logger.info(f"Fetching {name}...")
            df = pd.read_json(url)
            
            if not df.empty:
                df['ingested_at'] = get_utc_timestamp()
                
                filename = f"data/bronze/gov/{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                
                df.to_json(filename, orient='records', indent=2)
                logger.info(f"Saved {len(df)} records of {name} to {filename}")
            else:
                logger.warning(f"Fetched empty dataset for {name}")
                
    except Exception as e:
        logger.error(f"Error ingesting gov data: {str(e)}")

if __name__ == "__main__":
    ingest_gov_data()
