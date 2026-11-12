
import streamlit as st
import plotly.express as px
import pandas as pd
from loader import (load_shelter_data, load_spend_data, load_cluster_data, load_media_data,
                    load_pit_data, load_mission_data, load_news_items, load_community_items)

st.set_page_config(
    page_title="Chicago Migrant Resource Pulse",
    page_icon="🏙️",
    layout="wide"
)

# Sidebar Navigation
mode = st.sidebar.radio("Navigation", ["Overview", "Official 2026 Figures", "News & Community", "Population Analysis", "Financial Analysis", "Forecasting", "Crisis Pulse", "Data Export"])

st.title("🏙️ Chicago Migrant Resource Pulse")
st.markdown("---")

# Note: We will implement the sections one by one.
# For now, let's just show the raw data to ensure the loader works.

if mode == "Overview":
    st.header("Project Overview")
    st.markdown("""
    A combined view of **official City figures**, **local news**, and **community updates** on migrant and
    shelter resources in Chicago. News and community feeds update daily; official City datasets do not (see below).
    """)

    st.warning(
        "⚠️ **Data Notice**: The City's shelter-census data ends **Dec 31, 2024** and its new-arrivals "
        "vendor-payments data ends **Apr 24, 2025**. Anything shown after those dates in the Forecasting "
        "page is a model estimate, not an official figure. See **Official 2026 Figures** for the latest real counts."
    )

    shelter_df = load_shelter_data()
    spend_df = load_spend_data()
    pit_df = load_pit_data()
    news_df = load_news_items()

    col1, col2, col3, col4 = st.columns(4)

    if not pit_df.empty:
        latest = pit_df.sort_values('year').iloc[-1]
        prev = pit_df.sort_values('year').iloc[-2]
        col1.metric(f"People experiencing homelessness ({int(latest['year'])} PIT count)",
                    f"{int(latest['total']):,}", f"{int(latest['total'] - prev['total']):,} vs {int(prev['year'])}",
                    delta_color="inverse")

    if not shelter_df.empty:
        last = shelter_df.iloc[-1]
        col2.metric(f"Shelter census, last record ({last['date']:%b %d, %Y})", f"{last['total_population']:,.0f}")

    if not spend_df.empty:
        total_spend = spend_df['total_spend'].sum()
        col3.metric(f"Vendor spend, through {spend_df['date'].max():%b %d, %Y}", f"${total_spend/1e6:,.1f}M")

    if not news_df.empty:
        week = news_df[news_df['when'] >= news_df['when'].max() - pd.Timedelta(days=7)]
        col4.metric("News items, last 7 days", f"{len(week):,}")

    st.caption("Sources: City of Chicago DFSS 2026 Point-in-Time Count; City of Chicago Data Portal; "
               "Chicago Office of Inspector General (July 2026); public news RSS feeds.")
    st.info("Navigate using the sidebar to explore detailed analytics.")

elif mode == "Official 2026 Figures":
    st.header("Official Figures (Reference Data)")
    st.markdown("Hand-verified figures from published reports. These are annual or one-off, not daily feeds.")
    pit_df = load_pit_data()
    if not pit_df.empty:
        pit_df = pit_df.sort_values('year')
        long = pit_df.melt(id_vars='year', value_vars=['sheltered', 'unsheltered'],
                           var_name='Status', value_name='People')
        fig = px.bar(long, x='year', y='People', color='Status',
                     title='Chicago Point-in-Time homelessness count (one night each January)')
        st.plotly_chart(fig, use_container_width=True)
        latest = pit_df.iloc[-1]
        st.markdown(
            f"**{int(latest['year'])}:** {int(latest['total']):,} people "
            f"({int(latest['sheltered']):,} sheltered, {int(latest['unsheltered']):,} unsheltered). "
            "Counts from 2023 on include new arrivals/newcomers, and methodology changed in 2021; "
            "one-night counts understate people affected over a full year."
        )
        st.caption("Source: City of Chicago DFSS / UIC Voorhees Center, 2026 Point-in-Time Count & Survey Report, Appendix B, Table B-1.")
    mission = load_mission_data()
    if not mission.empty:
        st.subheader("New Arrivals Mission (Aug 2022 - Dec 2024)")
        st.dataframe(mission, use_container_width=True)
        st.caption("Source: Chicago Office of Inspector General, The City's Support of the New Arrivals Mission: An Explainer (July 22, 2026).")

elif mode == "News & Community":
    st.header("News & Community Updates")
    media = load_media_data()
    if not media.empty:
        recent = media[media['date'] >= media['date'].max() - pd.Timedelta(days=60)]
        fig = px.bar(recent, x='date', y=['news_count', 'social_count'], barmode='group',
                     title='Daily volume, last 60 days',
                     labels={'value': 'Items', 'variable': 'Type'})
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Latest news")
    news_df = load_news_items()
    if not news_df.empty:
        for _, r in news_df.head(15).iterrows():
            when = f"{r['when']:%b %d}" if pd.notna(r['when']) else ""
            st.markdown(f"- [{r['headline']}]({r['url']}) ({r['source']}, {when})")
    st.subheader("Community & nonprofit posts")
    com_df = load_community_items()
    if not com_df.empty:
        for _, r in com_df.head(10).iterrows():
            when = f"{r['when']:%b %d, %Y}" if pd.notna(r['when']) else ""
            st.markdown(f"- {str(r['content'])[:220]} ({r['source']}, {when})")
    st.caption("Collected from free public RSS feeds (news outlets, Bluesky, nonprofit blogs). Headlines link to the original publisher.")

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
    st.info("ℹ️ **Model estimates, not official figures.** The City's shelter census stopped at Dec 31, 2024, and "
            "the model was trained on a short history, so treat these projections with caution. Compare them with "
            "the official counts on the **Official 2026 Figures** page (the 2026 count found 6,527 people).")
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

