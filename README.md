# Chicago Migrant Resource Pulse

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chieac-chicago-migrant-resource-pulse.streamlit.app/)


## Mission
The **Chicago Migrant Resource Pulse** is a data engineering initiative designed to aggregate, process, and visualize information regarding migrant resources in Chicago. By unifying data from disparate sources—public government datasets, news outlets, and social media—we aim to provide a comprehensive "pulse" on shelter availability, aid distribution, and public sentiment to empower decision-makers and NGOs. News and organization updates are collected daily; official government figures are published far less often (see Data Context).


> [!IMPORTANT]
> **Data Context**: The City's open-data portal stopped updating the shelter census (last record **Dec 31, 2024**) and the new-arrivals vendor-payments data (last record **Apr 24, 2025**). The City's "new arrivals" mission formally ended on Dec 31, 2024 and its shelters were merged into one citywide system.
>
> Trends in the dashboard beyond those dates are **model-driven estimates from the Forecasting Module, not official figures**. Official 2026 figures that exist are kept in `data/reference/` (see *Reference Data* below) so the estimates can be compared against them. For example, the City's 2026 Point-in-Time Count found 6,527 people experiencing homelessness, down 12.4% from 2025 and 65.3% below the 2024 peak.

## Data Architecture
This project follows the **Medallion Architecture** pattern to organize data handling:

| Layer | Description | Format |
|-------|-------------|--------|
| **Bronze** | **Raw Ingestion**: Immutable landing zone for raw API responses (JSON) and scraped data (CSV/JSON). | JSON / CSV |
| **Silver** | **Cleaned & Standardized**: Deduplicated data with type casting, date standardization, and **PII removal** for privacy compliance. | Parquet |
| **Gold** | **Aggregated & Curated**: Business-level metrics and time-series data ready for dashboards and modeling. | CSV & Parquet |

## Tech Stack
- **Languages**: Python 3.12 (used by the automated workflows)
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
- Python 3.12 (the version used in CI)
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

### 3b. Automated Pipeline (GitHub Actions)
Two scheduled GitHub Actions workflows run the pipeline:
- `.github/workflows/daily_update.yml` (*Daily Data Pipeline*) runs every day at **6:00 AM CST** and commits updated gold-layer files.
- `.github/workflows/daily_ingest.yml` (*Daily Data Ingestion*) collects new raw data into `data/bronze/`.

Dependabot (`.github/dependabot.yml`) opens weekly pull requests for GitHub Actions and Python package updates.

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
6.  **Data Export**: Provides direct download access to the processed Gold Layer datasets (Shelter, Spend, Clusters).


## Data Outputs (Gold Layer)
After running the pipeline, you will find the following analytic datasets in `data/gold/`:
- **`daily_shelter_stats.csv`**: Total migrant population in shelters by date.
- **`daily_vendor_spend.csv`**: Total amount spent on vendor services by date.
- **`daily_media_volume.csv`**: Daily counts of news articles and social media posts (proxy for public discourse volume).
- **`daily_clusters.csv`**: Daily classification of resource demand (High/Medium/Low) based on population and spend.

## Predictive Modeling
The pipeline now includes an automated modeling stage:
1.  **Demand Forecasting**:
    - **Bridging the Transparency Gap**: With the City's shelter census and vendor-payment data dark since Dec 2024 / Apr 2025, our **LSTM (PyTorch)** models estimate later trends. These are projections. Annual official counts (e.g. the Point-in-Time Count) are available in `data/reference/` and should be used to check them.
    - **Methodology**: Models are trained on verified 2023-2024 data to project Shelter Population and Vendor Spend 90 days into the future.
    - Plots saved to `docs/images/`.
2.  **Clustering Analysis**:
    - Uses **K-Means** to segment days into operational categories (e.g., "High Strain Days").
    - Results visualized in `docs/images/clustering_results.png`.

## Reference Data
Sourced, hand-verified official figures live in `data/reference/`. They are annual or one-off reports, not daily feeds, and are updated manually when a new report is published.
- **`pit_counts_chicago.csv`**: Chicago Point-in-Time (PIT) homelessness counts, 2005-2026 (sheltered, unsheltered, total). Source: City of Chicago DFSS / UIC Voorhees Center, *2026 Point-in-Time Count & Survey Report*, Appendix B, Table B-1 ([DFSS PIT page](https://www.chicago.gov/city/en/depts/fss/provdrs/emerg/svcs/PITcount.html)). Methodology changed in 2021 (sampling), 2023-2024 (New Arrivals included) and 2025 (Newcomers); 2026 has no immigration-status breakdown. These are one-night counts and understate people experiencing homelessness over a full year.
- **`new_arrivals_mission.csv`**: Totals for the City's new-arrivals mission, Aug 31, 2022 to Dec 31, 2024: 46,282 people, $639,654,965 total spending, funding split and top-10 vendors. Source: Chicago Office of Inspector General, *The City's Support of the New Arrivals Mission: An Explainer* (July 22, 2026), [igchicago.org](https://igchicago.org/publications/new-arrivals-mission/).

## Technical Report (Week 6)
A comprehensive academic paper detailing the methodology, architecture, and modeling results of this project is available:
- 📄 **[Read the Academic Paper](docs/academic_paper.md)**

## Governance & Ethics
This project adheres to strict ethical guidelines:
- **Privacy First**: Personally Identifiable Information (PII) is stripped at the Silver layer.
- **Aggregated Reporting**: Public outputs are aggregated to prevent re-identification.
- **Transparency**: All data sources are public or ethically scraped.
See `docs/data_governance_ethics.md` for full details.
