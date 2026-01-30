# The Chicago Migrant Resource Pulse: A Data-Driven Approach to Crisis Management and Resource Allocation

**Author:** Adithya D M  
**Date:** January 2026  
**Repository:** [https://github.com/adithyadaine/chiEAC-chicago-migrant-resource-pulse]

---

## Abstract

The Chicago migrant crisis has presented significant logistical and humanitarian challenges, exacerbated by fragmented data sources and a sudden cessation of official government reporting in December 2024. The **Chicago Migrant Resource Pulse** is a comprehensive data engineering and data science initiative designed to address this transparency gap. By implementing a Medallion Architecture data pipeline, this project aggregates disparate real-time data from government portals, news media, and social networks. Furthermore, it employs Long Short-Term Memory (LSTM) networks for demand forecasting and K-Means clustering for operational strain classification. This paper details the technical architecture, data governance methodologies, and predictive modeling results that empower decision-makers to anticipate resource needs through 2026.

## 1. Introduction

Since late 2022, Chicago has received a significant influx of migrants, straining city resources, shelter capacity, and support services. Effective crisis response requires accurate, timely data. However, the ecosystem of information has been characterized by silos: official census counts, sporadic news reports, and unverified social media narratives.

The challenge intensified in December 2024 when official detailed reporting on shelter populations and vendor spending largely ceased, creating a "data blackout." This project was conceived to:
1.  **Centralize Truth:** Build a unified data lake from remaining public sources.
2.  **Bridge the Gap:** Use machine learning to forecast trends into the blackout period (2025-2026).
3.  **Operationalize Insights:** Provide a real-time dashboard for NGOs and city planners.

## 2. Methodology: Data Engineering Architecture

This project adopts a **Lakehouse** paradigm, structured around the **Medallion Architecture** to ensure data quality and lineage.

### 2.1 Data Ingestion (Bronze Layer)
The ingestion layer aims for high-fidelity capture of raw data. We employed a multi-source strategy:
-   **Government Data**: Automated API calls to the City of Chicago Data Portal to fetch historical shelter census and spending records.
-   **News Media**: A custom `BeautifulSoup` scraper targets local news outlets (e.g., Chicago Tribune, Sun-Times) to quantify public discourse volume.
-   **Social Media**: Selenium-based scrapers capture sentiment and volume proxies from public social timelines.

All data is stored in its native format (JSON/CSV) in the **Bronze Layer**, serving as an immutable record.

### 2.2 Data Processing (Silver Layer)
Data in the Silver Layer is cleaned, standardized, and enriched. Key transformations include:
-   **Schema Enforcement**: Casting loose string types to strict DateTime and Float32 formats.
-   **De-duplication**: Handling overlapping records from multi-day scrapes.
-   **Privacy preservation (PII)**: Although the source data is aggregate, we implement strict hashing on any potential identifiers to comply with ethical guidelines.
-   **Storage**: Data is serialized to **Parquet**, optimizing for compression and query performance.

### 2.3 Aggregation (Gold Layer)
The Gold Layer is business-level data ready for consumption. We generate four primary tables:
1.  **`daily_shelter_stats`**: Time-series of population counts.
2.  **`daily_vendor_spend`**: Aggregate daily spending on vendors (staffing, food, etc.).
3.  **`daily_media_volume`**: Normalized counts of news and social posts.
4.  **`daily_clusters`**: Output of the clustering model (see Section 3.2).

## 3. Predictive Modeling & Analysis

To address the post-2024 data gap, we developed two primary machine learning capabilities.

### 3.1 Demand Forecasting (LSTM)
We utilized **Long Short-Term Memory (LSTM)** networks, a type of Recurrent Neural Network (RNN) well-suited for time-series data with temporal dependencies.

*   **Training Data**: Verified daily shelter population and spending data from Jan 2023 - Dec 2024.
*   **Architecture**: A stacked LSTM model with dropout regularization to prevent overfitting on the relatively short historical window.
*   **Objective**: Forecast the next 90 days of resource demand.
*   **Performance**: The model achieves a Mean Absolute Percentage Error (MAPE) of <15% on the validation set, successfully capturing the seasonal fluctuations observed during winter months.

### 3.2 Operational Strain Clustering (K-Means)
To simplify complex metrics into actionable status indicators, we applied **K-Means Clustering**.
*   **Features**: Daily Population, Daily Spend, and Media Volume.
*   **Optimum K**: Using the Elbow Method, we determined $k=3$ as the optimal cluster count.
*   **Interpretation**:
    *   **Cluster 0 (Low Strain)**: Stable population, low media attention.
    *   **Cluster 1 (Medium Strain)**: Rising population, moderate spending.
    *   **Cluster 2 (High Strain)**: Peak population, high spending spikes, and elevated media discourse.

## 4. Results & Visualization

The final output is served via a **Streamlit** dashboard, offering:
-   **Crisis Pulse**: A color-coded indicator of the current day's cluster (Green/Yellow/Red).
-   **Forecast Views**: Overlaying the LSTM predictions (dashed lines) onto historical trends (solid lines), clearly demarcating the "Official Data" vs. "Projected" eras.
-   **Geospatial Analysis**: Mapping shelter locations (using historical address data) to visualize geographic concentration.

## 5. Conclusion & Future Work

The **Chicago Migrant Resource Pulse** demonstrates how modern data engineering can restore visibility during information blackouts. By combining robust pipelining with predictive modeling, we provide a tool that not only records history but anticipates future needs.

**Future directions include:**
-   **Sentiment Analysis**: Integrating NLP models to score the *tone* of news articles, not just volume.
-   **Resource Matching**: A recommendation engine to match specific shelter needs (e.g., "baby formula") with donor offers.
-   **Cloud Deployment**: Migrating the local pipeline to AWS/GCP for true serverless automation.

## 6. References
1.  City of Chicago Data Portal. (2023-2024). *Migrant Shelter Census*.
2.  Hochreiter, S., & Schmidhuber, J. (1997). "Long Short-Term Memory". *Neural Computation*.
3.  Databricks. "The Medallion Architecture".
