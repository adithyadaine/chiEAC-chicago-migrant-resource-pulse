import os
import glob
import pandas as pd
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils import setup_logger

logger = setup_logger('gold_aggregates', 'logs/gold_aggregates.log')

def create_gold_layer():
    silver_gov_path = 'data/silver/gov/'
    silver_news_path = 'data/silver/news/'
    silver_social_path = 'data/silver/social/'
    gold_path = 'data/gold/'
    os.makedirs(gold_path, exist_ok=True)
    
    # --- 1. Daily Shelter Stats ---
    logger.info("Aggregating Shelter Census data...")
    census_files = glob.glob(os.path.join(silver_gov_path, 'shelter_census_*.parquet'))
    if census_files:
        try:
            dfs = [pd.read_parquet(f) for f in census_files]
            census_df = pd.concat(dfs, ignore_index=True)
            
            # Determine cols
            date_col = next((c for c in census_df.columns if pd.api.types.is_datetime64_any_dtype(census_df[c])), None)
            if not date_col:
                 date_col = next((c for c in census_df.columns if 'date' in c.lower()), None)
            
            # Look for count column
            count_col = next((c for c in census_df.columns if 'count' in c.lower() or 'population' in c.lower() or 'total_staying' in c.lower()), None)
            
            if date_col and count_col:
                # Ensure proper datetime
                if not pd.api.types.is_datetime64_any_dtype(census_df[date_col]):
                    census_df[date_col] = pd.to_datetime(census_df[date_col])
                    
                census_df['date_norm'] = census_df[date_col].dt.date
                daily_shelter = census_df.groupby('date_norm')[count_col].sum().reset_index()
                daily_shelter.columns = ['date', 'total_population']
                daily_shelter['date'] = pd.to_datetime(daily_shelter['date']) # Ensure timestamp for parquet consistency
                
                out_file = os.path.join(gold_path, 'daily_shelter_stats.parquet')
                daily_shelter.to_parquet(out_file, index=False)
                
                # Also save as CSV for sharing (Gold Layer Req)
                csv_file = os.path.join(gold_path, 'daily_shelter_stats.csv')
                daily_shelter.to_csv(csv_file, index=False)
                logger.info(f"Created {out_file} and {csv_file} with {len(daily_shelter)} rows")
            else:
                logger.warning(f"Cols not found in shelter data. Date: {date_col}, Count: {count_col}")
        except Exception as e:
            logger.error(f"Error aggregation shelter data: {e}")
    else:
        logger.warning("No Shelter Census files found in Silver.")

    # --- 2. Daily Spending ---
    logger.info("Aggregating Vendor Payments data...")
    payment_files = glob.glob(os.path.join(silver_gov_path, 'vendor_payments_*.parquet'))
    if payment_files:
        try:
            dfs = [pd.read_parquet(f) for f in payment_files]
            pay_df = pd.concat(dfs, ignore_index=True)
            
            # Cols
            date_col = next((c for c in pay_df.columns if pd.api.types.is_datetime64_any_dtype(pay_df[c])), None)
            if not date_col:
                 date_col = next((c for c in pay_df.columns if 'date' in c.lower()), None)
            
            amount_col = next((c for c in pay_df.columns if 'amount' in c.lower()), None)
            
            if date_col and amount_col:
                 if not pd.api.types.is_datetime64_any_dtype(pay_df[date_col]):
                    pay_df[date_col] = pd.to_datetime(pay_df[date_col])
                    
                 pay_df['date_norm'] = pay_df[date_col].dt.date
                 daily_spend = pay_df.groupby('date_norm')[amount_col].sum().reset_index()
                 daily_spend.columns = ['date', 'total_spend']
                 daily_spend['date'] = pd.to_datetime(daily_spend['date'])
                 
                 out_file = os.path.join(gold_path, 'daily_vendor_spend.parquet')
                 daily_spend.to_parquet(out_file, index=False)
                 
                 # Also save as CSV for sharing
                 csv_file = os.path.join(gold_path, 'daily_vendor_spend.csv')
                 daily_spend.to_csv(csv_file, index=False)
                 logger.info(f"Created {out_file} and {csv_file} with {len(daily_spend)} rows")
            else:
                logger.warning(f"Cols not found in vendor data. Date: {date_col}, Amount: {amount_col}")
        except Exception as e:
            logger.error(f"Error aggregating payment data: {e}")
    else:
        logger.warning("No Vendor Payments files found in Silver.")

    # --- 3. Daily News/Social Volume ---
    logger.info("Aggregating Media Volume...")
    
    # News
    news_files = glob.glob(os.path.join(silver_news_path, '*.parquet'))
    news_counts = pd.DataFrame()
    if news_files:
        try:
            dfs = [pd.read_parquet(f) for f in news_files]
            news_df = pd.concat(dfs, ignore_index=True)
            if not news_df.empty:
                date_col = next((c for c in news_df.columns if pd.api.types.is_datetime64_any_dtype(news_df[c])), None)
                if date_col:
                    news_df['date_norm'] = news_df[date_col].dt.date
                    news_counts = news_df.groupby('date_norm').size().reset_index(name='news_count')
                    news_counts.rename(columns={'date_norm': 'date'}, inplace=True)
                    news_counts['date'] = pd.to_datetime(news_counts['date'])
        except Exception as e:
            logger.error(f"Error aggregating news: {e}")

    # Social
    social_files = glob.glob(os.path.join(silver_social_path, '*.parquet'))
    social_counts = pd.DataFrame()
    if social_files:
        try:
            dfs = [pd.read_parquet(f) for f in social_files]
            social_df = pd.concat(dfs, ignore_index=True)
            if not social_df.empty:
                date_col = next((c for c in social_df.columns if pd.api.types.is_datetime64_any_dtype(social_df[c])), None)
                if date_col:
                     social_df['date_norm'] = social_df[date_col].dt.date
                     social_counts = social_df.groupby('date_norm').size().reset_index(name='social_count')
                     social_counts.rename(columns={'date_norm': 'date'}, inplace=True)
                     social_counts['date'] = pd.to_datetime(social_counts['date'])
        except Exception as e:
            logger.error(f"Error aggregating social: {e}")
    
    # Merge
    if not news_counts.empty and not social_counts.empty:
        volume = pd.merge(news_counts, social_counts, on='date', how='outer').fillna(0)
    elif not news_counts.empty:
        volume = news_counts
        volume['social_count'] = 0
    elif not social_counts.empty:
        volume = social_counts
        volume['news_count'] = 0
    else:
        volume = pd.DataFrame(columns=['date', 'news_count', 'social_count'])
        
    if not volume.empty:
        volume.sort_values('date', inplace=True)
        int_cols = ['news_count', 'social_count']
        volume[int_cols] = volume[int_cols].astype(int)
        
        out_file = os.path.join(gold_path, 'daily_media_volume.parquet')
        volume.to_parquet(out_file, index=False)
        
        # Also save as CSV for sharing
        csv_file = os.path.join(gold_path, 'daily_media_volume.csv')
        volume.to_csv(csv_file, index=False)
        logger.info(f"Created {out_file} and {csv_file} with {len(volume)} rows")
    else:
        logger.warning("No media data to aggregate.")

if __name__ == "__main__":
    create_gold_layer()
