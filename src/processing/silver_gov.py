import os
import glob
import pandas as pd
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.processing.cleaning import standardize_date, clean_currency
from src.utils import setup_logger

logger = setup_logger('silver_gov', 'logs/silver_gov.log')

def process_gov_data():
    bronze_path = 'data/bronze/gov/'
    silver_path = 'data/silver/gov/'
    os.makedirs(silver_path, exist_ok=True)
    
    # --- Process Vendor Payments ---
    payment_files = glob.glob(os.path.join(bronze_path, 'vendor_payments_*.json'))
    logger.info(f"Found {len(payment_files)} vendor payment files.")
    
    for file_path in payment_files:
        try:
            logger.info(f"Processing {file_path}")
            df = pd.read_json(file_path)
            
            if df.empty:
                logger.warning(f"Skipping empty file {file_path}")
                continue
                
            # Standardize columns if possible, but mainly value cleaning
            if 'amount' in df.columns:
                df['amount'] = df['amount'].apply(clean_currency)
            elif 'amount_dollars' in df.columns:
                df['amount_dollars'] = df['amount_dollars'].apply(clean_currency)
            
            # Identify date columns
            date_cols = [c for c in df.columns if 'date' in c.lower()]
            for col in date_cols:
                df[col] = df[col].apply(standardize_date)
            
            # Save as Parquet
            base_name = os.path.basename(file_path).replace('.json', '.parquet')
            out_file = os.path.join(silver_path, base_name)
            df.to_parquet(out_file, index=False)
            logger.info(f"Saved to {out_file}")
            
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")

    # --- Process Shelter Census ---
    census_files = glob.glob(os.path.join(bronze_path, 'shelter_census_*.json'))
    logger.info(f"Found {len(census_files)} shelter census files.")
    
    for file_path in census_files:
        try:
            logger.info(f"Processing {file_path}")
            df = pd.read_json(file_path)
            
            if df.empty:
                continue
            
            # Clean Dates
            for col in df.columns:
                if 'date' in col.lower():
                    df[col] = df[col].apply(standardize_date)
            
            # Ensure count is numeric
            for col in df.columns:
                lower_col = col.lower()
                if 'count' in lower_col or 'population' in lower_col or 'total_staying' in lower_col:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

            base_name = os.path.basename(file_path).replace('.json', '.parquet')
            out_file = os.path.join(silver_path, base_name)
            df.to_parquet(out_file, index=False)
            logger.info(f"Saved to {out_file}")
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    process_gov_data()
