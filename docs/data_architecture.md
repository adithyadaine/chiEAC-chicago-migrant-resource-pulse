# Data Architecture: Medallion Pattern

## 1. Overview
This project follows the **Medallion Architecture**, organizing data into three progressively cleaner and more valuable layers.

### Bronze Layer (Raw Ingestion)
- **Content:** Raw JSON, HTML, CSVs directly as scraped/downloaded.
- **Source:** Web scrapers, API responses.
- **Immutability:** Data here is immutable; purely a landing zone.
- **Format:** Parquet (preferred for compression) or raw JSON/CSV.

### Silver Layer (Cleaned & Standardized)
- **Content:** Deduplicated, cleaned, and standardized data.
- **Transformations:**
    - Timestamp normalization (UTC).
    - Categorical mapping (e.g., standardizing "Food Drive" variations).
    - Null handling.
    - PII removal.
- **Format:** Parquet / SQLite tables.

### Gold Layer (Curated & Aggregated)
- **Content:** Business-level aggregates ready for visualization and modeling.
- **Examples:**
    - `daily_sentiment_by_neighborhood`
    - `resource_availability_trends`
    - `forecast_model_features`
- **Format:** CSV (for easy sharing) / SQL Views.

## 2. Technology Stack
- **Language:** Python 3.10+
- **Ingestion:** `requests`, `BeautifulSoup4`, `selenium`, `pandas`
- **Orchestration:** Simple Cron jobs or GitHub Actions (Week 2 decision).
- **Processing:** `pandas`, `duckdb` (for local SQL-like processing).
- **Storage:** Local filesystem (simulating Data Lake) organized by layer.
- **Modeling:** `scikit-learn`, `statsmodels` (ARIMA), `nltk`/`spacy`.

## 3. Directory Schema for Data (Local)
The `data/` directory (ignored by git) will mirror this structure:
```
data/
├── bronze/
│   ├── news/
│   ├── social/
│   └── gov/
├── silver/
│   ├── ...
└── gold/
    ├── ...
```
