import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title(" National Budget Analysis")

# --- Section 1: DPWH Budget Over Time ---
st.header("DPWH Budget Trend (2011-2025)")
try:
    # Read directly from the Excel file and specific sheet
    df_summary = pd.read_excel(
        "data/DPWH_budget_consolidated.xlsx", 
        sheet_name="WIP - DPWH Budget Summary 2011-"
    )
    
    df_summary['AMOUNT'] = pd.to_numeric(df_summary['AMOUNT'], errors='coerce')
    yearly_budget = df_summary.groupby('FISCAL YEAR')['AMOUNT'].sum().reset_index()
    
    fig_yearly = px.line(
        yearly_budget,
        x='FISCAL YEAR',
        y='AMOUNT',
        title="Total DPWH Budget per Year (GAA)",
        markers=True,
        template='plotly_white'
    )
    st.plotly_chart(fig_yearly, use_container_width=True)
except Exception as e:
    st.warning(f"Could not load historical budget data from 'DPWH_budget_consolidated.xlsx'. Error: {e}")

st.markdown("---")

# --- Section 2: Proposed (NEP) vs. Approved (GAA) Budget ---
st.header("2025 Proposed (NEP) vs. Approved (GAA) Budget")
try:
    df_nep_gaa = pd.read_excel(
        "data/NEP v GAA Comparison.xlsx",
        sheet_name="Sheet1" # Assuming it's the first sheet
    )
    # The first column might not have a name, so we access it by position
    df_dpwh_nep_gaa = df_nep_gaa[df_nep_gaa.iloc[:, 0].str.contains('DPWH', na=False)].copy()
    df_dpwh_nep_gaa.columns = ['Program', 'NEP', 'GAA', 'Variance']
    
    # Clean the program names
    df_dpwh_nep_gaa['Program'] = df_dpwh_nep_gaa['Program'].str.replace('-', '').str.strip()
    
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
except Exception as e:
    st.warning(f"Could not load budget comparison data from 'NEP v GAA Comparison.xlsx'. Error: {e}")
