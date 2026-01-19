
import streamlit as st
import plotly.express as px
import pandas as pd
from loader import load_shelter_data, load_spend_data, load_cluster_data

st.set_page_config(
    page_title="Chicago Migrant Resource Pulse",
    page_icon="🏙️",
    layout="wide"
)

# Sidebar Navigation
mode = st.sidebar.radio("Navigation", ["Overview", "Population Analysis", "Financial Analysis", "Forecasting", "Crisis Pulse", "Data Export"])

st.title("🏙️ Chicago Migrant Resource Pulse")
st.markdown("---")

# Note: We will implement the sections one by one.
# For now, let's just show the raw data to ensure the loader works.

if mode == "Overview":
    st.header("Project Overview")
    st.markdown("""
    This dashboard provides a real-time 'pulse' on the migrant resource situation in Chicago.
    
    ### Key Metrics
    """)
    
    st.warning("⚠️ **Data Notice**: Official City of Chicago reporting for this dataset ceased in **December 2024**. Recent trends may be based on predictive modeling.")
    
    shelter_df = load_shelter_data()
    spend_df = load_spend_data()
    
    col1, col2, col3 = st.columns(3)
    
    if not shelter_df.empty:
        latest_pop = shelter_df.iloc[-1]['total_population']
        col1.metric("Current Shelter Population", f"{latest_pop:,.0f}")
        
    if not spend_df.empty:
        total_spend = spend_df['total_spend'].sum()
        col2.metric("Total Vendor Spend", f"${total_spend:,.2f}")

    col3.metric("Data Source", "City of Chicago")
    
    st.info("Navigate using the sidebar to explore detailed analytics.")

elif mode == "Population Analysis":
    st.header("Shelter Population Trends")
    df = load_shelter_data()
    if not df.empty:
        fig = px.line(df, x='date', y='total_population', title='Total Shelter Population Over Time')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No shelter data available.")

elif mode == "Financial Analysis":
    st.header("Vendor Spend Trends")
    df = load_spend_data()
    if not df.empty:
        fig = px.bar(df, x='date', y='total_spend', title='Daily Vendor Spend')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No spend data available.")

elif mode == "Forecasting":
    st.header("Predictive Forecasts")
    st.info("ℹ️ **Transparency Bridge**: Due to the government data blackout (post-Dec 2024), these **LSTM Projections** provide the primary insight into current resource demands.")
    st.markdown("Here we will visualize the LSTM and Linear Regression forecasts generated in Week 4.")
    # Placeholder for loading the images generated in Week 4
    
    # Example of loading the saved images from docs/images
    import os
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'docs', 'images')
    forecast_img = os.path.join(docs_dir, 'forecast_results.png')
    
    if os.path.exists(forecast_img):
        st.image(forecast_img, caption="Population Forecast (LSTM vs Linear vs Actual)")
    else:
        st.warning("Forecast image not found. Please run the modeling pipeline first.")


elif mode == "Crisis Pulse":
    st.header("Crisis Severity Clustering")
    df = load_cluster_data()
    if not df.empty:
        # Create interactive scatter plot
        fig = px.scatter(
            df,
            x="total_population",
            y="total_spend",
            color="cluster",
            title="Crisis Severity Clusters: Population vs. Spend",
            labels={
                "total_population": "Total Shelter Population",
                "total_spend": "Daily Vendor Spend ($)",
                "cluster": "Crisis Cluster"
            },
            hover_data=["date"],
            color_continuous_scale=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Recent Data")
        st.dataframe(df.tail(10))
    else:
        st.warning("No clustering data available.")

elif mode == "Data Export":
    st.header("Data Export")
    st.markdown("Download the processed Gold Layer datasets for your own analysis.")
    
    shelter_df = load_shelter_data()
    spend_df = load_spend_data()
    cluster_df = load_cluster_data()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Shelter Population")
        st.metric("Records", len(shelter_df))
        if not shelter_df.empty:
            csv = shelter_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="daily_shelter_stats.csv",
                mime="text/csv",
            )
            
    with col2:
        st.subheader("Vendor Spend")
        st.metric("Records", len(spend_df))
        if not spend_df.empty:
            csv = spend_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="daily_vendor_spend.csv",
                mime="text/csv",
            )
            
    with col3:
        st.subheader("Crisis Clusters")
        st.metric("Records", len(cluster_df))
        if not cluster_df.empty:
            csv = cluster_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="daily_clusters.csv",
                mime="text/csv",
            )

