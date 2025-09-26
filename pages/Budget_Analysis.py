import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(layout="wide")
st.title(" National Budget Analysis")
st.markdown("This page analyzes the DPWH budget over time, with a focus on flood management and comparisons to the national budget.")

# --- Helper function to clean currency strings ---
def clean_currency(value):
    if isinstance(value, str):
        return pd.to_numeric(value.replace(',', ''), errors='coerce')
    return pd.to_numeric(value, errors='coerce')

# --- Section 1: DPWH Budget Over Time ---
st.header("DPWH Budget Trend (2011-2025)")
try:
    # This file provides the historical summary
    df_summary = pd.read_csv("data/DPWH_budget_consolidated.xlsx - WIP - DPWH Budget Summary 2011-.csv")
    
    df_summary['AMOUNT'] = clean_currency(df_summary['AMOUNT'])
    yearly_budget = df_summary.groupby('FISCAL YEAR')['AMOUNT'].sum().reset_index()
    
    fig_yearly = px.line(
        yearly_budget,
        x='FISCAL YEAR',
        y='AMOUNT',
        title="Total DPWH Budget per Year (GAA)",
        labels={'FISCAL YEAR': 'Year', 'AMOUNT': 'Budget (in PHP)'},
        markers=True,
        template='plotly_white'
    )
    fig_yearly.update_layout(yaxis_title="Budget (in PHP Billions)", yaxis_tickformat=",.0s")
    st.plotly_chart(fig_yearly, use_container_width=True)
    st.info("This chart shows the total approved budget (GAA) for the DPWH across three administrations, illustrating the significant growth in funding.")

except FileNotFoundError:
    st.error("Could not find 'DPWH_budget_consolidated.xlsx - WIP - DPWH Budget Summary 2011-.csv'. Please make sure it is in the 'data' folder.")

st.markdown("---")

# --- Section 2: Proposed (NEP) vs. Approved (GAA) Budget ---
st.header("2025 Proposed (NEP) vs. Approved (GAA) Budget")
st.markdown("This section highlights changes made to the DPWH budget during the legislative process, showing the variance between the President's proposal (NEP) and the final approved budget (GAA).")

try:
    df_nep_gaa = pd.read_csv("data/NEP v GAA Comparison.xlsx - Sheet1.csv")
    df_dpwh_nep_gaa = df_nep_gaa[df_nep_gaa.iloc[:, 0].str.contains('DPWH', na=False)].copy()
    df_dpwh_nep_gaa.columns = ['Program', 'NEP', 'GAA', 'Variance']
    
    # Clean and convert columns to numeric
    for col in ['NEP', 'GAA', 'Variance']:
        df_dpwh_nep_gaa[col] = clean_currency(df_dpwh_nep_gaa[col])
    
    # Clean the program names
    df_dpwh_nep_gaa['Program'] = df_dpwh_nep_gaa['Program'].str.replace('-', '').str.strip()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Comparison by Program Area")
        df_melted = df_dpwh_nep_gaa.melt(id_vars='Program', value_vars=['NEP', 'GAA'], var_name='BudgetType', value_name='Amount')
        fig_nep_gaa = px.bar(df_melted, x='Amount', y='Program', color='BudgetType', barmode='group', orientation='h', template='plotly_white')
        fig_nep_gaa.update_layout(xaxis_title="Budget (in PHP)", yaxis_title=None, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_nep_gaa, use_container_width=True)

    with col2:
        st.subheader("Variance Analysis (GAA minus NEP)")
        fig_variance = px.bar(df_dpwh_nep_gaa, x='Variance', y='Program', orientation='h', color='Variance', color_continuous_scale='RdBu', template='plotly_white')
        fig_variance.update_layout(xaxis_title="Change in Budget (PHP)", yaxis_title=None, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_variance, use_container_width=True)

except FileNotFoundError:
    st.error("Could not find 'NEP v GAA Comparison.xlsx - Sheet1.csv'. Please make sure it is in the 'data' folder.")
    
st.markdown("---")

# --- Section 3: DPWH Budget vs. Other Departments ---
st.header("DPWH vs. Other National Agencies (2025 GAA)")
try:
    # Read the data, skipping the first few rows to get to the header
    df_nga = pd.read_csv("data/NGAs Budget per FY.xlsx - TOTAL GAA per Agency.csv", header=4)
    df_2025_nga = df_nga[['AGENCY NAME', '2025']].dropna()
    df_2025_nga.columns = ['Agency', 'Budget']
    
    # The budget is in thousands, so multiply by 1000
    df_2025_nga['Budget'] = clean_currency(df_2025_nga['Budget']) * 1000
    
    top_10_agencies = df_2025_nga.nlargest(10, 'Budget')
    
    st.subheader("Top 10 Government Agencies by Budget")
    fig_top_agencies = px.bar(
        top_10_agencies,
        x='Budget',
        y='Agency',
        orientation='h',
        title='2025 Approved Budget for Top 10 Agencies',
        template='plotly_white'
    )
    fig_top_agencies.update_layout(xaxis_title="Budget (in PHP Billions)", yaxis_title=None, xaxis_tickformat=",.0s", yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top_agencies, use_container_width=True)
    st.info("This chart puts the DPWH's budget into perspective, comparing it with other major government departments like Education, Health, and Defense.")

except FileNotFoundError:
    st.error("Could not find 'NGAs Budget per FY.xlsx - TOTAL GAA per Agency.csv'. Please make sure it is in the 'data' folder.")
