import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(layout="wide")
st.title(" National Budget Analysis")
st.markdown("This page analyzes the DPWH budget over time, with a focus on flood management and comparisons to the national budget.")

# --- Helper function to clean currency strings ---
def clean_currency(value):
    # Converts various formats to a numeric type, returning NaN if it fails
    if isinstance(value, str):
        value = value.replace(',', '')
    return pd.to_numeric(value, errors='coerce')

# --- Section 1: DPWH Budget Over Time ---
st.header("DPWH Budget Trend (2011-2025)")
try:
    df_summary = pd.read_excel(
        "data/DPWH_budget_consolidated.xlsx", 
        sheet_name="WIP - DPWH Budget Summary 2011-"
    )
    df_summary['AMOUNT'] = clean_currency(df_summary['AMOUNT'])
    yearly_budget = df_summary.groupby('FISCAL YEAR')['AMOUNT'].sum().reset_index()
    
    fig_yearly = px.line(
        yearly_budget, x='FISCAL YEAR', y='AMOUNT',
        title="Total DPWH Budget per Year (GAA)", markers=True, template='plotly_white'
    )
    fig_yearly.update_layout(yaxis_title="Budget (in PHP Billions)", yaxis_tickformat=",.0s", xaxis_title="Fiscal Year")
    st.plotly_chart(fig_yearly, use_container_width=True)

except Exception as e:
    st.error(f"""
    **Error loading historical budget data.**
    - Please ensure the file `data/DPWH_budget_consolidated.xlsx` exists.
    - Make sure it contains a sheet named exactly `WIP - DPWH Budget Summary 2011-`.
    - Error details: {e}
    """)

st.markdown("---")

# --- Section 2: Proposed (NEP) vs. Approved (GAA) Budget ---
st.header("2025 Proposed (NEP) vs. Approved (GAA) Budget")
try:
    df_nep_gaa = pd.read_excel(
        "data/NEP v GAA Comparison.xlsx",
        sheet_name="Sheet1",
        header=0
    )
    df_nep_gaa.columns = ['Program', 'NEP', 'GAA', 'Variance']
    
    df_nep_gaa['Program'] = df_nep_gaa['Program'].astype(str)
    df_dpwh_nep_gaa = df_nep_gaa[df_nep_gaa['Program'].str.contains('DPWH', na=False)].copy()

    for col in ['NEP', 'GAA', 'Variance']:
        df_dpwh_nep_gaa[col] = clean_currency(df_dpwh_nep_gaa[col])
    
    df_dpwh_nep_gaa['Program'] = df_dpwh_nep_gaa['Program'].str.replace('-', '').str.strip()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Comparison by Program")
        df_melted = df_dpwh_nep_gaa.melt(id_vars='Program', value_vars=['NEP', 'GAA'], var_name='BudgetType', value_name='Amount')
        fig_nep_gaa = px.bar(df_melted, x='Amount', y='Program', color='BudgetType', barmode='group', orientation='h', template='plotly_white', title="2025 Proposed vs. Approved Budget")
        fig_nep_gaa.update_layout(xaxis_title="Budget (in PHP)", yaxis_title=None, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_nep_gaa, use_container_width=True)

    with col2:
        st.subheader("Variance Analysis (GAA minus NEP)")
        fig_variance = px.bar(df_dpwh_nep_gaa, x='Variance', y='Program', orientation='h', color='Variance', color_continuous_scale='RdBu', template='plotly_white', title="Budget Changes During Legislation")
        fig_variance.update_layout(xaxis_title="Change in Budget (PHP)", yaxis_title=None, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_variance, use_container_width=True)

except Exception as e:
    st.error(f"""
    **Error loading budget comparison data.**
    - Please ensure the file `data/NEP v GAA Comparison.xlsx` exists.
    - Make sure it contains a sheet named `Sheet1` where the first row is the header.
    - Error details: {e}
    """)
    
st.markdown("---")

# --- Section 3: DPWH Budget vs. Other Departments ---
st.header("DPWH vs. Other National Agencies (2025 GAA)")
try:
    # This new logic is more robust and finds the header row automatically.
    df_nga_raw = pd.read_excel(
        "data/NGAs Budget per FY.xlsx",
        sheet_name="TOTAL GAA per Agency",
        header=None
    )
    
    # Find the row that contains 'AGENCY NAME' to use as the header
    header_row_index = None
    for i, row in df_nga_raw.iterrows():
        if 'AGENCY NAME' in str(row.values):
            header_row_index = i
            break
            
    if header_row_index is not None:
        # Set the correct header and drop the rows above it
        df_nga = df_nga_raw.iloc[header_row_index:].reset_index(drop=True)
        df_nga.columns = df_nga.iloc[0]
        df_nga = df_nga.drop(0).reset_index(drop=True)
        
        # Now proceed with the cleaned dataframe
        df_2025_nga = df_nga[['AGENCY NAME', 2025]].dropna()
        df_2025_nga.columns = ['Agency', 'Budget']
        
        # The budget is in thousands, so multiply by 1000
        df_2025_nga['Budget'] = clean_currency(df_2025_nga['Budget']) * 1000
        
        top_10_agencies = df_2025_nga.nlargest(10, 'Budget')
        
        st.subheader("Top 10 Government Agencies by Budget")
        fig_top_agencies = px.bar(
            top_10_agencies, x='Budget', y='Agency', orientation='h',
            title='2025 Approved Budget for Top 10 Agencies', template='plotly_white'
        )
        fig_top_agencies.update_layout(xaxis_title="Budget (in PHP Billions)", yaxis_title=None, xaxis_tickformat=",.0s", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_top_agencies, use_container_width=True)
    else:
        st.error("Could not automatically find the header row ('AGENCY NAME') in the 'TOTAL GAA per Agency' sheet.")

except Exception as e:
    st.error(f"""
    **Error loading national agency data.**
    - Please ensure the file `data/NGAs Budget per FY.xlsx` exists.
    - Make sure it contains a sheet named `TOTAL GAA per Agency`.
    - Error details: {e}
    """)
