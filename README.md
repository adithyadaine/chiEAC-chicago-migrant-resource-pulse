# Chicago Migrant Resource Pulse

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chieac-chicago-migrant-resource-pulse.streamlit.app/)


## Mission
The **Chicago Migrant Resource Pulse** is a data engineering initiative designed to aggregate, process, and visualize information regarding migrant resources in Chicago. By unifying data from disparate sources—public government datasets, news outlets, and community/nonprofit updates—we aim to provide a comprehensive "pulse" on shelter availability, aid distribution, and public discourse to empower decision-makers and NGOs. News and organization updates are collected daily; official government figures are published far less often (see Data Context).


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
- **Ingestion**: Requests (government APIs and free public RSS/Atom feeds)
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
1.  **Ingests** data from configured sources (City data portal API, news RSS feeds, community/nonprofit feeds). The run stops with an error if government or news data is missing; community feeds only warn.
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
The **Research Interface** (Week 5) provides the following views:

1.  **Overview**: Latest official count (2026 Point-in-Time), last shelter-census and vendor-spend figures with their dates, and recent news volume.
2.  **Official 2026 Figures**: Point-in-Time counts 2005-2026 and the Inspector General's new-arrivals mission totals, from `data/reference/`.
3.  **News & Community**: Daily news/community volume plus the latest headlines and nonprofit posts.
4.  **Population Analysis**: Time series of the City's shelter census (through Dec 2024).
5.  **Financial Analysis**: Daily vendor spending (through Apr 2025).
6.  **Forecasting**: The **LSTM & Linear Regression** model estimates, clearly labelled as estimates.
7.  **Crisis Pulse**: Daily cluster classifications (High/Medium/Low Strain).
8.  **Data Export**: Download the Gold Layer datasets (Shelter, Spend, Clusters).


## Data Outputs (Gold Layer)
After running the pipeline, you will find the following analytic datasets in `data/gold/`:
- **`daily_shelter_stats.csv`**: Total people in the City's emergency shelters by date, from the City's shelter census (only 19 dates, May 13 to Dec 31, 2024, because that is all the City published).
- **`daily_vendor_spend.csv`**: Total amount spent on new-arrivals vendor services by invoice date (totals about $639.6M, matching the City's source data and the Inspector General).
- **`daily_media_volume.csv`**: Daily counts of news articles and community/nonprofit posts (proxy for public discourse volume).
- **`latest_news.csv`** / **`latest_community.csv`**: The newest headlines and community posts, used by the dashboard's *News & Community* page.
- **`daily_clusters.csv`**: Daily classification of resource demand (High/Medium/Low) based on population and spend.

## Predictive Modeling
The pipeline now includes an automated modeling stage:
1.  **Demand Forecasting**:
    - **Bridging the Transparency Gap**: With the City's shelter census and vendor-payment data dark since Dec 2024 / Apr 2025, our **LSTM (PyTorch)** models estimate later trends. These are projections. Annual official counts (e.g. the Point-in-Time Count) are available in `data/reference/` and should be used to check them.
    - **Methodology**: Models are trained on the City's published shelter census (19 dates, May 13 to Dec 31, 2024) and vendor payments (invoices through Apr 24, 2025), and project Shelter Population and Vendor Spend 90 days ahead. The shelter history is very short, so forecasts are rough (the shelter model's error was about 3,000 people in a recent run); treat them as illustrative.
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
