#!/bin/bash

# Chicago Migrant Resource Pulse - Daily Ingestion Job

echo "============================================"
echo "Starting Ingestion Pipeline: $(date)"
echo "============================================"

# Ensure we are in the project root (optional safety check)
# cd /path/to/project

echo "[1/7] Running News Scraper..."
python3 src/ingestion/news_scraper.py

echo "[2/7] Running Government Data Ingestion..."
python3 src/ingestion/gov_data_ingest.py

echo "[3/7] Running Social Media Scraper (Nitter)..."
python3 src/ingestion/social_scraper.py

echo "--------------------------------------------"
echo "Ingestion Complete. Starting Processing..."
echo "--------------------------------------------"

echo "[4/7] Running Silver Layer Processing (Gov)..."
python3 src/processing/silver_gov.py

echo "[5/7] Running Silver Layer Processing (News)..."
python3 src/processing/silver_news.py

echo "[6/7] Running Silver Layer Processing (Social)..."
python3 src/processing/silver_social.py

echo "[7/7] Running Gold Layer Aggregation..."
python3 src/processing/gold_aggregates.py

echo "============================================"
echo "Pipeline Finished: $(date)"
echo "============================================"