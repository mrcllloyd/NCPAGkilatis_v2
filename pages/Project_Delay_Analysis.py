import streamlit as st
import plotly.express as px
from utils import load_project_data

st.set_page_config(layout="wide")
st.title("Project Timeline and Delay Analysis")

df = load_project_data()

if df is not None:
    st.subheader("Top 20 Most Delayed Projects")
    top_delayed = df[df['ProjectDelay'] > 0].nlargest(20, 'ProjectDelay')
    top_delayed['ProjectLabel'] = top_delayed['ProjectDescription'].str[:70] + '... (' + top_delayed['Province'] + ')'
    
    fig = px.bar(top_delayed, x='ProjectDelay', y='ProjectLabel', orientation='h', color='ProjectDelay', color_continuous_scale=px.colors.sequential.OrRd, template='plotly_white')
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribution of Project Delays")
        fig2 = px.histogram(df[df['ProjectDelay'] > 0], x='ProjectDelay', nbins=50, template='plotly_white')
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        st.subheader("Average Delay by Region")
        avg_delay_region = df[df['ProjectDelay'] > 0].groupby('Region')['ProjectDelay'].mean().sort_values().reset_index()
        fig3 = px.bar(avg_delay_region, x='ProjectDelay', y='Region', orientation='h', template='plotly_white')
        st.plotly_chart(fig3, use_container_width=True)
