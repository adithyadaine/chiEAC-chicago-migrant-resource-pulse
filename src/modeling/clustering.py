import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils import setup_logger

logger = setup_logger('clustering', 'logs/clustering.log')

def run_clustering():
    # Since we might not have granular facility-level data in Silver (based on previous file checks, 
    # it seemed Silver was just cleaned versions), we will perform time-series clustering on the Gold daily data
    # to classify "types of days" (e.g., High Stress, Normal, Low Activity).
    
    gold_path = 'data/gold/'
    shelter_file = os.path.join(gold_path, 'daily_shelter_stats.parquet')
    spend_file = os.path.join(gold_path, 'daily_vendor_spend.parquet')
    media_file = os.path.join(gold_path, 'daily_media_volume.parquet')
    
    if not (os.path.exists(shelter_file) and os.path.exists(spend_file)):
        logger.error("Missing Gold layer files for clustering.")
        return

    logger.info("Loading data for clustering...")
    shelter_df = pd.read_parquet(shelter_file)
    spend_df = pd.read_parquet(spend_file)
    
    # Merge
    # FIX: Use outer join to keep all days. 
    # Shelter pop is continuous (ffill), Spend is sparse (fillna 0).
    df = pd.merge(shelter_df, spend_df, on='date', how='outer')
    df = df.sort_values('date')
    
    # Fill missing values
    df['total_population'] = df['total_population'].ffill().bfill() # Assume stable population
    df['total_spend'] = df['total_spend'].fillna(0) # Assume no invoice = 0 spend
    
    if os.path.exists(media_file):
        media_df = pd.read_parquet(media_file)
        df = pd.merge(df, media_df, on='date', how='left').fillna(0)
    
    # Drop rows that might still be empty if any
    df = df.dropna(subset=['total_population'])
    
    if df.empty:
        logger.warning("Merged dataframe is empty after outer join.")
        return

    # Features for clustering
    features = ['total_population', 'total_spend']
    if 'news_count' in df.columns:
        features += ['news_count', 'social_count']
        
    X = df[features]
    
    # Normalize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # K-Means
    if len(df) < 3:
        logger.warning(f"Not enough data for clustering (n={len(df)}). Skipping.")
        return

    k = min(3, len(df))
    logger.info(f"Running K-Means with k={k}...")
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Analyze Clusters
    logger.info("Cluster Centers (Scaled):")
    logger.info(kmeans.cluster_centers_)
    
    summary = df.groupby('cluster')[features].mean()
    logger.info("Cluster Summaries (Mean Values):")
    logger.info(summary)
    
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.scatter(df['total_population'], df['total_spend'], c=df['cluster'], cmap='viridis', s=50, alpha=0.7)
    plt.title('Clustering of Days: Population vs. Spend')
    plt.xlabel('Total Population')
    plt.ylabel('Total Spend')
    plt.colorbar(label='Cluster')
    
    output_dir = 'docs/images'
    os.makedirs(output_dir, exist_ok=True)
    plot_path = os.path.join(output_dir, 'clustering_results.png')
    plt.savefig(plot_path)
    logger.info(f"Clustering plot saved to {plot_path}")
    
    # Save clustered data
    out_file = os.path.join(gold_path, 'daily_clusters.csv')
    df.to_csv(out_file, index=False)
    logger.info(f"Clustered data saved to {out_file}")

if __name__ == "__main__":
    run_clustering()
