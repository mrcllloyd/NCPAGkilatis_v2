import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("National Budget Analysis")

# Section 1: DPWH Budget Over Time
st.header("DPWH Budget Trend (2011-2025)")
try:
    df_summary = pd.read_csv("data/DPWH_budget_consolidated.xlsx - WIP - DPWH Budget Summary 2011-.csv")
    df_summary['AMOUNT'] = pd.to_numeric(df_summary['AMOUNT'], errors='coerce')
    yearly_budget = df_summary.groupby('FISCAL YEAR')['AMOUNT'].sum().reset_index()
    fig_yearly = px.line(yearly_budget, x='FISCAL YEAR', y='AMOUNT', title="Total DPWH Budget per Year (GAA)", markers=True, template='plotly_white')
    st.plotly_chart(fig_yearly, use_container_width=True)
except FileNotFoundError:
    st.warning("Could not find 'DPWH_budget_consolidated.xlsx - WIP - DPWH Budget Summary 2011-.csv'. Skipping this section.")

st.markdown("---")

# Section 2: NEP vs. GAA
st.header("2025 Proposed (NEP) vs. Approved (GAA) Budget")
try:
    df_nep_gaa = pd.read_csv("data/NEP v GAA Comparison.xlsx - Sheet1.csv")
    df_dpwh_nep_gaa = df_nep_gaa[df_nep_gaa.iloc[:, 0].str.contains('DPWH', na=False)]
    df_dpwh_nep_gaa.columns = ['Program', 'NEP', 'GAA', 'Variance']
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Comparison by Program")
        df_melted = df_dpwh_nep_gaa.melt(id_vars='Program', value_vars=['NEP', 'GAA'], var_name='BudgetType', value_name='Amount')
        fig_nep_gaa = px.bar(df_melted, x='Amount', y='Program', color='BudgetType', barmode='group', orientation='h', template='plotly_white')
        fig_nep_gaa.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_nep_gaa, use_container_width=True)
    with col2:
        st.subheader("Variance Analysis (GAA minus NEP)")
        fig_variance = px.bar(df_dpwh_nep_gaa, x='Variance', y='Program', orientation='h', color='Variance', color_continuous_scale='RdBu', template='plotly_white')
        fig_variance.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_variance, use_container_width=True)
except FileNotFoundError:
    st.warning("Could not find 'NEP v GAA Comparison.xlsx - Sheet1.csv'. Skipping this section.")
