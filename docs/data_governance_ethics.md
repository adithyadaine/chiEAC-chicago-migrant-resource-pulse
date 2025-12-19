# Data Governance & Ethics Policy

## 1. Data Privacy & Sensitivity
Given the vulnerable nature of the population being studied (migrants, asylum seekers, and refugees), strict data privacy measures must be enforced.
- **PII Stripping:** No Personally Identifiable Information (Names, specific addresses of individuals, phone numbers) will be stored in the Silver or Gold layers.
- **Anonymization:** Data will be aggregated to the neighborhood or zip code level whenever possible to prevent re-identification.
- **Restricted Access:** Raw data (Bronze layer) containing potential PII will be restricted and not published publicly.

## 2. Data Sources & Compliance
- **Public Data:** Chicago.gov data usage will comply with their Open Data Terms of Use.
- **Social Media:** Scraping will be respectful of rate limits and terms of service. We will prioritize public pages/groups and avoid joining private groups to scrape data without consent.
- **News Articles:** Content will be used for NLP analysis (sentiment/keyword extraction) under Fair Use for research/educational purposes. Full text will not be republished; only derived metrics and snippets.

## 3. Data Retention
- **Raw Data (Bronze):** Retained for the duration of the project for debugging, then archived/deleted post-publication if it contains sensitive info.
- **Processed Data (Gold):** Retained indefinitely as an open-source dataset for research.

## 4. Security
- Repository will not contain API keys or credentials (`.gitignore` enforcement).
- Sensitive raw data files will not be committed to GitHub.

## 5. Ethics of Prediction
- Predictive models will be audited for bias to ensure they do not negatively stereotype migrant populations or suggest discriminatory resource allocation.
- "Sentiment Analysis" will be contextualized as a measure of public discourse, not an endorsement of specific viewpoints.
