# Chicago Migrant Resource Pulse

## Mission
The **Chicago Migrant Resource Pulse** is a data engineering initiative designed to aggregate, process, and visualize real-time information regarding migrant resources in Chicago. By unifying data from disparate sources—public government datasets, news outlets, and social media—we aim to provide a comprehensive "pulse" on shelter availability, aid distribution, and public sentiment to empower decision-makers and NGOs.

## Data Architecture
This project follows the **Medallion Architecture** pattern to organize data handling:

| Layer | Description | Format |
|-------|-------------|--------|
| **Bronze** | **Raw Ingestion**: Immutable landing zone for raw API responses (JSON) and scraped data (CSV/JSON). | JSON / CSV |
| **Silver** | **Cleaned & Standardized**: Deduplicated data with type casting, date standardization, and **PII removal** for privacy compliance. | Parquet |
| **Gold** | **Aggregated & Curated**: Business-level metrics and time-series data ready for dashboards and modeling. | CSV & Parquet |

## Tech Stack
- **Languages**: Python 3.10+
- **Data Processing**: Pandas, NumPy, PyArrow
- **Machine Learning**: 
    - **PyTorch** (LSTM Forecating)
    - **Scikit-learn** (K-Means Clustering, Linear Regression)
- **Ingestion**: Requests, BeautifulSoup4, Selenium
- **Orchestration**: Shell scripting (`run_ingestion.sh`)

## Project Structure
```
├── data/                   # Data Lake (Local)
│   ├── bronze/             # Raw data from scrapers/APIs
│   ├── silver/             # Cleaned Parquet files
│   └── gold/               # Aggregated metrics (CSV/Parquet)
├── docs/                   # Project documentation (Charter, Architecture, Governance)
├── src/
│   ├── ingestion/          # Scripts for fetching raw data (Gov, News, Social)
│   ├── processing/         # Scripts for Silver/Gold layer transformations
│   ├── modeling/           # ★ NEW: Forecasting & Clustering models
│   └── utils.py            # Shared utilities (logging, timestamping)
├── run_ingestion.sh        # Main pipeline entry point
└── requirements.txt        # Python dependencies
```

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Chrome (for Selenium-based scrapers)

### 2. Installation
It is recommended to use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Pipeline
The `run_ingestion.sh` script orchestrates the entire workflow:
1.  **Ingests** data from configured sources.
2.  **Processes** data into the Silver layer (cleaning & PII stripping).
3.  **Aggregates** metrics into the Gold layer.

```bash
./run_ingestion.sh
```

### 4. Running the Dashboard (Week 5)
To launch the interactive Streamlit dashboard:

```bash
./run_dashboard.sh
```

## Interactive Dashboard Features
The new **Research Interface** (Week 5) provides a comprehensive view of the data pipeline:

1.  **Overview**: High-level KPIs including current shelter population and total vendor spend.
2.  **Population Analysis**: Interactive time-series trends of migrant population across all shelters.
3.  **Financial Analysis**: Breakdown of daily vendor spending to track resource allocation.
4.  **Forecasting**: Visualizes the **LSTM & Linear Regression** models, projecting demand 90 days into the future.
5.  **Crisis Pulse**: Displays daily cluster classifications (High/Medium/Low Strain) to identify critical operational periods.


## Data Outputs (Gold Layer)
After running the pipeline, you will find the following analytic datasets in `data/gold/`:
- **`daily_shelter_stats.csv`**: Total migrant population in shelters by date.
- **`daily_vendor_spend.csv`**: Total amount spent on vendor services by date.
- **`daily_media_volume.csv`**: Daily counts of news articles and social media posts (proxy for public discourse volume).
- **`daily_clusters.csv`**: Daily classification of resource demand (High/Medium/Low) based on population and spend.

## Predictive Modeling
The pipeline now includes an automated modeling stage:
1.  **Demand Forecasting**:
    - Uses **LSTM (PyTorch)** and Linear Regression to predict future Shelter Population and Vendor Spend.
    - Bridged Forecast: Dynamically fills the gap from the last government data release (Dec 2024/Apr 2025) to the present day (Jan 2026) and projects **90 days** into the future.
    - Plots saved to `docs/images/`.
2.  **Clustering Analysis**:
    - Uses **K-Means** to segment days into operational categories (e.g., "High Strain Days").
    - Results visualized in `docs/images/clustering_results.png`.

## Governance & Ethics
This project adheres to strict ethical guidelines:
- **Privacy First**: Personally Identifiable Information (PII) is stripped at the Silver layer.
- **Aggregated Reporting**: Public outputs are aggregated to prevent re-identification.
- **Transparency**: All data sources are public or ethically scraped.
See `docs/data_governance_ethics.md` for full details.
