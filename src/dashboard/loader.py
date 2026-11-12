
import pandas as pd
import streamlit as st
import os

# Define base path to data
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
GOLD_DIR = os.path.join(DATA_DIR, 'gold')

@st.cache_data
def load_shelter_data():
    """Loads daily shelter statistics from the Gold layer."""
    filepath = os.path.join(GOLD_DIR, 'daily_shelter_stats.csv')
    if not os.path.exists(filepath):
        st.error(f"Data file not found: {filepath}")
        return pd.DataFrame()
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    return df

@st.cache_data
def load_spend_data():
    """Loads daily vendor spend data from the Gold layer."""
    filepath = os.path.join(GOLD_DIR, 'daily_vendor_spend.csv')
    if not os.path.exists(filepath):
        st.error(f"Data file not found: {filepath}")
        return pd.DataFrame()
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    return df

@st.cache_data
def load_media_data():
    """Loads daily media volume data from the Gold layer."""
    filepath = os.path.join(GOLD_DIR, 'daily_media_volume.csv')
    if not os.path.exists(filepath):
        return pd.DataFrame()
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    return df

@st.cache_data
def load_cluster_data():
    """Loads daily clustering analysis from the Gold layer."""
    filepath = os.path.join(GOLD_DIR, 'daily_clusters.csv')
    if not os.path.exists(filepath):
        return pd.DataFrame()
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    return df

REFERENCE_DIR = os.path.join(DATA_DIR, 'reference')
SILVER_DIR = os.path.join(DATA_DIR, 'silver')

@st.cache_data
def load_pit_data():
    """Official Point-in-Time homelessness counts (data/reference)."""
    filepath = os.path.join(REFERENCE_DIR, 'pit_counts_chicago.csv')
    if not os.path.exists(filepath):
        return pd.DataFrame()
    return pd.read_csv(filepath)

@st.cache_data
def load_mission_data():
    """Totals from the Inspector General's new-arrivals mission report (data/reference)."""
    filepath = os.path.join(REFERENCE_DIR, 'new_arrivals_mission.csv')
    if not os.path.exists(filepath):
        return pd.DataFrame()
    return pd.read_csv(filepath)

@st.cache_data
def load_news_items():
    """Latest news articles (Gold: latest_news.csv)."""
    filepath = os.path.join(GOLD_DIR, 'latest_news.csv')
    if not os.path.exists(filepath):
        return pd.DataFrame()
    df = pd.read_csv(filepath)
    df['when'] = pd.to_datetime(df['when'], errors='coerce')
    return df.sort_values('when', ascending=False)

@st.cache_data
def load_community_items():
    """Latest community / nonprofit posts (Gold: latest_community.csv)."""
    filepath = os.path.join(GOLD_DIR, 'latest_community.csv')
    if not os.path.exists(filepath):
        return pd.DataFrame()
    df = pd.read_csv(filepath)
    df['when'] = pd.to_datetime(df['when'], errors='coerce')
    return df.sort_values('when', ascending=False)
