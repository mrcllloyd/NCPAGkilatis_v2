import streamlit as st
import plotly.express as px
from utils import load_project_data # Import the function

# Page Config
st.set_page_config(
    page_title="NCPAGkilatis Dashboard",
    layout="wide"
)

# Load Data
df = load_project_data()

# Header
st.title("NCPAGkilatis: DPWH Project Dashboard")
st.markdown("Welcome! This dashboard provides an overview of DPWH projects. Use the sidebar to explore different analyses.")
st.markdown("---")

if df is not None:
    # KPIs
    st.header("National Overview")
    total_projects = df.shape[0]
    total_cost = df['ContractCost'].sum()
    avg_delay = df[df['ProjectDelay'] > 0]['ProjectDelay'].mean()
    total_overdue_projects = df[df['ProjectDelay'] > 0].shape[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Projects Analyzed", f"{total_projects:,}")
    col2.metric("Total Investment", f"₱{(total_cost / 1e9):,.2f}B")
    col3.metric("Projects with Delays", f"{total_overdue_projects:,} ({total_overdue_projects/total_projects:.1%})")
    col4.metric("Average Delay Duration", f"{avg_delay:,.0f} days")

    st.markdown("---")

    # Homepage Charts
    st.header("High-Level Insights")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Total Investment by Region")
        region_spending = df.groupby('Region')['ContractCost'].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(region_spending, x='ContractCost', y='Region', orientation='h', title="Total Contract Cost per Region", template='plotly_white')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Projects by Presidential Administration")
        term_counts = df['PresTerm'].value_counts().reset_index()
        fig2 = px.pie(term_counts, names='PresTerm', values='count', title='Number of Projects Initiated per Term', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Awaiting data file to be loaded.")
