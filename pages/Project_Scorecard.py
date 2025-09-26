import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_project_data

st.set_page_config(layout="wide")
st.title("Project Scorecard & Outlier Analysis")
st.markdown("""
This page moves beyond simple totals to identify potential red flags. It scores entities based on a combination of risk factors 
to highlight areas that may warrant further investigation.
""")

df = load_project_data()

if df is not None:
    # --- Calculate additional metrics needed for scoring ---
    df['CostUnderrunPct'] = ((df['ApprovedBudgetForTheContract'] - df['ContractCost']) / df['ApprovedBudgetForTheContract']) * 100
    # Handle cases where budget is zero to avoid infinite values
    df['CostUnderrunPct'] = df['CostUnderrunPct'].fillna(0)
    df.loc[df['ApprovedBudgetForTheContract'] == 0, 'CostUnderrunPct'] = 0

    # --- Scorecard Calculation ---
    st.header("Risk Factor Scorecard")
    score_type = st.selectbox("Select entity to analyze:", ["Provinces", "Implementing Offices", "Contractors"])

    if score_type == "Provinces":
        agg_col = 'Province'
    elif score_type == "Implementing Offices":
        agg_col = 'ImplementingOffice'
    else:
        agg_col = 'Contractor'

    # Aggregate basic metrics
    scorecard = df.groupby(agg_col).agg(
        Total_Projects=('ProjectID', 'count'),
        Total_Contract_Value=('ContractCost', 'sum'),
        Average_Delay_Days=('ProjectDelay', 'mean'),
        Avg_Cost_Underrun_Pct=('CostUnderrunPct', 'mean')
    ).reset_index()

    # Calculate "Suspiciously Low Underrun" metric (e.g., projects where savings are less than 1%)
    low_underrun_df = df[df['CostUnderrunPct'] < 1]
    low_underrun_counts = low_underrun_df.groupby(agg_col).size().reset_index(name='Low_Underrun_Projects')
    
    # Calculate "Contract Concentration" (value of top 3 contractors as % of total)
    def get_concentration(group):
        if len(group) < 3:
            return 100.0
        top_3_value = group.groupby('Contractor')['ContractCost'].sum().nlargest(3).sum()
        total_value = group['ContractCost'].sum()
        return (top_3_value / total_value) * 100 if total_value > 0 else 0

    concentration = df.groupby(agg_col).apply(get_concentration).reset_index(name='Top_3_Contractor_Concentration_Pct')

    # Merge all metrics into the final scorecard
    scorecard = pd.merge(scorecard, low_underrun_counts, on=agg_col, how='left')
    scorecard = pd.merge(scorecard, concentration, on=agg_col, how='left')
    scorecard = scorecard.fillna(0)
    
    # Calculate percentage of projects with low underrun
    scorecard['Low_Underrun_Pct_of_Projects'] = (scorecard['Low_Underrun_Projects'] / scorecard['Total_Projects']) * 100
    
    # Display the scorecard
    st.dataframe(
        scorecard.sort_values(by='Total_Contract_Value', ascending=False),
        column_config={
            "Total_Contract_Value": st.column_config.NumberColumn(format="₱%.0f"),
            "Average_Delay_Days": st.column_config.ProgressColumn(
                "Avg. Delay (Days)",
                help="Average project delay in days. Higher is worse.",
                min_value=0, max_value=int(scorecard['Average_Delay_Days'].max()),
            ),
            "Avg_Cost_Underrun_Pct": st.column_config.ProgressColumn(
                "Avg. Savings (%)",
                help="Average percentage saved from the approved budget. Consistently low values can be a red flag.",
                min_value=0, max_value=int(scorecard['Avg_Cost_Underrun_Pct'].max()),
            ),
            "Top_3_Contractor_Concentration_Pct": st.column_config.ProgressColumn(
                "Contract Concentration (%)",
                help="Percentage of total contract value awarded to the top 3 contractors. Higher values suggest less competition.",
                min_value=0, max_value=100,
            ),
            "Low_Underrun_Pct_of_Projects": st.column_config.ProgressColumn(
                "Low Savings Projects (%)",
                help="Percentage of projects with less than 1% budget savings.",
                min_value=0, max_value=100,
            ),
        },
        use_container_width=True
    )
    
    st.markdown("---")

    # --- Deep Dive Section ---
    st.header("Deep Dive Analysis")
    selected_entity = st.selectbox(f"Select a {score_type.rstrip('s')} for a detailed breakdown:", scorecard[agg_col])

    if selected_entity:
        entity_df = df[df[agg_col] == selected_entity]
        
        st.write(f"### Analysis for: **{selected_entity}**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top 5 Delayed Projects")
            delayed = entity_df[entity_df['ProjectDelay'] > 0].nlargest(5, 'ProjectDelay')
            if delayed.empty:
                st.write("No delayed projects found.")
            else:
                fig = px.bar(delayed, y='ProjectDescription', x='ProjectDelay', orientation='h', template='plotly_white', title="Days Overdue")
                fig.update_layout(yaxis={'title': None, 'autorange': 'reversed'}, xaxis={'title': 'Days'})
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Contractor Distribution")
            contractor_dist = entity_df.groupby('Contractor')['ContractCost'].sum().nlargest(5).reset_index()
            fig2 = px.pie(contractor_dist, names='Contractor', values='ContractCost', title="Top 5 Contractors by Contract Value")
            st.plotly_chart(fig2, use_container_width=True)
