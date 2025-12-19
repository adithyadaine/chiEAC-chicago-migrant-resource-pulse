#!/bin/bash

# Chicago Migrant Resource Pulse - Daily Ingestion Job

echo "============================================"
echo "Starting Ingestion Pipeline: $(date)"
echo "============================================"

# Ensure we are in the project root (optional safety check)
# cd /path/to/project

echo "[1/3] Running News Scraper..."
python3 src/ingestion/news_scraper.py

echo "[2/3] Running Government Data Ingestion..."
python3 src/ingestion/gov_data_ingest.py

echo "[3/3] Running Social Media Scraper (Nitter)..."
python3 src/ingestion/social_scraper.py

echo "============================================"
echo "Pipeline Finished: $(date)"
echo "============================================"
