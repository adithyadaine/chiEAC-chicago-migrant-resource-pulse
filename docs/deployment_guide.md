# Deployment Guide: Chicago Migrant Resource Pulse

This dashboard is built with **Streamlit** and can be easily deployed for free using **Streamlit Community Cloud**.

## 1. Prerequisites
- A [GitHub](https://github.com/) account.
- The project code pushed to a GitHub repository (which we have done).

## 2. Deploy to Streamlit Community Cloud

1.  **Sign Up/Login**: Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.
2.  **New App**: Click the **"New app"** button.
3.  **Connect Repository**:
    - Select your repository: `chiEAC-chicago-migrant-resource-pulse`
    - **Branch**: Select `setup/week-5-research-interface` (or `main` if you merged).
    - **Main file path**: Enter `src/dashboard/app.py`
4.  **Deploy**: Click **"Deploy!"**.

## 3. Configuration (Optional)
The dashboard reads data directly from the `data/gold/` directory in the repository.
- **Updates**: To update the dashboard with new data, run the local pipeline (`./run_ingestion.sh`), commit the updated CSVs in `data/gold`, and push to GitHub. The live dashboard will update automatically.

## 4. Troubleshooting
- **Dependencies**: Streamlit Cloud will automatically install packages from `requirements.txt`.
- **Paths**: The application uses relative paths, so it should work out-of-the-box.
