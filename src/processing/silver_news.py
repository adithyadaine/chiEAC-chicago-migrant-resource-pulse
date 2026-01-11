import os
import glob
import pandas as pd
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.processing.cleaning import clean_text, standardize_date
from src.utils import setup_logger

logger = setup_logger('silver_news', 'logs/silver_news.log')

def process_news_data():
    bronze_path = 'data/bronze/news/'
    silver_path = 'data/silver/news/'
    os.makedirs(silver_path, exist_ok=True)
    
    all_files = glob.glob(os.path.join(bronze_path, '*.json'))
    all_files += glob.glob(os.path.join(bronze_path, '*.csv'))
    if not all_files:
        logger.info("No news files found to process.")
        return

    dfs = []
    logger.info(f"Found {len(all_files)} news files. Consolidating...")
    
    for f in all_files:
        try:
            if f.endswith('.json'):
                df = pd.read_json(f)
            else:
                df = pd.read_csv(f)
                
            if not df.empty:
                dfs.append(df)
        except Exception as e:
            logger.error(f"Error reading {f}: {e}")
    
    if not dfs:
        return

    full_df = pd.concat(dfs, ignore_index=True)
    logger.info(f"Total records before cleaning: {len(full_df)}")
    
    # Cleaning
    if 'title' in full_df.columns:
        full_df['title'] = full_df['title'].apply(clean_text)
    
    # Common content columns
    for col in ['content', 'body', 'description']:
        if col in full_df.columns:
            full_df[col] = full_df[col].apply(clean_text)
            
    # Dates
    for col in ['published_at', 'date', 'scraped_at']:
        if col in full_df.columns:
            full_df[col] = full_df[col].apply(standardize_date)
        
    # Deduplicate
    subset_cols = []
    if 'url' in full_df.columns:
        subset_cols.append('url')
    elif 'title' in full_df.columns:
        subset_cols.append('title')
        
    if subset_cols:
        before = len(full_df)
        full_df.drop_duplicates(subset=subset_cols, keep='last', inplace=True)
        after = len(full_df)
        logger.info(f"Deduplication complete: {before} -> {after} records")
        
    # Save compacted Silver dataset
    # In a real scenario, we might partition by date, but for now a single file
    # or overwriting the consolidated view is fine for the scale.
    out_file = os.path.join(silver_path, 'news_silver.parquet')
    full_df.to_parquet(out_file, index=False)
    logger.info(f"Saved consolidated silver news to {out_file}")

if __name__ == "__main__":
    process_news_data()
