import os
import glob
import pandas as pd
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.processing.cleaning import clean_text, standardize_date
from src.utils import setup_logger

logger = setup_logger('silver_social', 'logs/silver_social.log')

def process_social_data():
    bronze_path = 'data/bronze/social/'
    silver_path = 'data/silver/social/'
    os.makedirs(silver_path, exist_ok=True)
    
    all_files = glob.glob(os.path.join(bronze_path, '*.json'))
    if not all_files:
        logger.info("No social files found.")
        return

    dfs = []
    logger.info(f"Found {len(all_files)} social data files.")
    
    for f in all_files:
        try:
            df = pd.read_json(f)
            if not df.empty:
                dfs.append(df)
        except Exception as e:
            logger.error(f"Error reading {f}: {e}")
    
    if not dfs:
        return

    full_df = pd.concat(dfs, ignore_index=True)
    logger.info(f"Total social records: {len(full_df)}")
    
    # Cleaning
    # Look for common text fields
    for col in ['content', 'text', 'message', 'caption']:
        if col in full_df.columns:
            full_df[col] = full_df[col].apply(clean_text)
            
    # Dates
    for col in ['created_at', 'timestamp', 'date', 'posted_at']:
        if col in full_df.columns:
            full_df[col] = full_df[col].apply(standardize_date)
            
    # Normalize hashtags
    if 'hashtags' in full_df.columns:
        full_df['hashtags'] = full_df['hashtags'].astype(str)

    # Dedup
    if 'id' in full_df.columns:
        full_df.drop_duplicates(subset=['id'], keep='last', inplace=True)
    elif 'url' in full_df.columns:
        full_df.drop_duplicates(subset=['url'], keep='last', inplace=True)
    else:
        full_df.drop_duplicates(inplace=True)

    # Privacy Compliance: Remove PII
    pii_cols = ['username', 'author', 'user_id', 'display_name', 'user']
    cols_to_drop = [c for c in pii_cols if c in full_df.columns]
    if cols_to_drop:
        full_df.drop(columns=cols_to_drop, inplace=True)
        logger.info(f"Dropped PII columns: {cols_to_drop}")

    out_file = os.path.join(silver_path, 'social_silver.parquet')
    full_df.to_parquet(out_file, index=False)
    logger.info(f"Saved silver social data to {out_file}")

if __name__ == "__main__":
    process_social_data()
