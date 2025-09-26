import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_project_data

st.set_page_config(layout="wide")
st.title("Contractor Performance Analysis")

df = load_project_data()

if df is not None:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 15 Contractors by Project Count")
        contractor_counts = df['Contractor'].value_counts().nlargest(15).reset_index()
        fig = px.bar(contractor_counts, x='count', y='Contractor', orientation='h', template='plotly_white')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Top 15 Contractors by Total Contract Value")
        contractor_value = df.groupby('Contractor')['ContractCost'].sum().nlargest(15).reset_index()
        fig2 = px.bar(contractor_value, x='ContractCost', y='Contractor', orientation='h', template='plotly_white')
        fig2.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    
    st.subheader("Deep Dive into a Specific Contractor")
    all_contractors = sorted(df['Contractor'].unique())
    selected_contractor = st.selectbox("Select a Contractor", options=all_contractors)

    if selected_contractor:
        contractor_df = df[df['Contractor'] == selected_contractor]
        avg_delay = contractor_df[contractor_df['ProjectDelay'] > 0]['ProjectDelay'].mean()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Projects", f"{contractor_df.shape[0]}")
        c2.metric("Total Contract Value", f"₱{(contractor_df['ContractCost'].sum()/1e6):.2f}M")
        c3.metric("Average Project Delay", f"{avg_delay:.0f} days" if not pd.isna(avg_delay) else "No Delays")
        st.dataframe(contractor_df[['ProjectDescription', 'Region', 'ContractCost', 'ProjectDelay']].sort_values(by='ProjectDelay', ascending=False))
