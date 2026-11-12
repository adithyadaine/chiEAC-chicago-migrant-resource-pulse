#!/bin/bash

# Chicago Migrant Resource Pulse - Daily Ingestion Job

echo "============================================"
echo "Starting Ingestion Pipeline: $(date)"
echo "============================================"

# Ensure we are in the project root (optional safety check)
# cd /path/to/project

# Fail loudly: scrapers log errors but exit 0, so we check that this run
# actually produced fresh data. Government + news are required; social is optional.
MARKER=$(mktemp)
FAILED=0

# Returns success if a non-trivial file matching $2 was written in $1 during this run
fresh_file() {
    [ -n "$(find "$1" -name "$2" -newer "$MARKER" -size +10c 2>/dev/null | head -1)" ]
}

echo "[1/7] Running News Scraper..."
python3 src/ingestion/news_scraper.py

echo "[2/7] Running Government Data Ingestion..."
for attempt in 1 2 3; do
    python3 src/ingestion/gov_data_ingest.py
    if fresh_file data/bronze/gov 'vendor_payments_*.json' && fresh_file data/bronze/gov 'shelter_census_*.json'; then
        break
    fi
    echo "WARNING: government data incomplete (attempt $attempt of 3)"
    [ "$attempt" -lt 3 ] && sleep 60
done

echo "[3/7] Running Community Feed Scraper (Bluesky + nonprofit blogs)..."
python3 src/ingestion/social_scraper.py

# --- Freshness checks ---
if ! fresh_file data/bronze/news '*'; then
    echo "ERROR: news scraper produced no new data"; FAILED=1
fi
if ! fresh_file data/bronze/gov 'vendor_payments_*.json'; then
    echo "ERROR: no new vendor payments data from the City data portal"; FAILED=1
fi
if ! fresh_file data/bronze/gov 'shelter_census_*.json'; then
    echo "ERROR: no new shelter census data from the City data portal"; FAILED=1
fi
if ! fresh_file data/bronze/social '*'; then
    echo "WARNING: social scraper produced no new data (non-fatal)"
fi
if [ "$FAILED" -ne 0 ]; then
    echo "Ingestion failed. Stopping before processing so existing outputs are not overwritten."
    exit 1
fi

echo "--------------------------------------------"
echo "Ingestion Complete. Starting Processing..."
echo "--------------------------------------------"

set -e
echo "[4/7] Running Silver Layer Processing (Gov)..."
python3 src/processing/silver_gov.py

echo "[5/7] Running Silver Layer Processing (News)..."
python3 src/processing/silver_news.py

echo "[6/7] Running Silver Layer Processing (Social)..."
python3 src/processing/silver_social.py

echo "[7/7] Running Gold Layer Aggregation..."
python3 src/processing/gold_aggregates.py

echo "[8/8] Running Predictive Modeling & Analysis..."
python3 src/modeling/forecasting.py
python3 src/modeling/clustering.py

echo "============================================"
echo "Pipeline Finished: $(date)"
echo "============================================"
