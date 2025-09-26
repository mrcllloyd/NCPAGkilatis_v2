import streamlit as st
import plotly.express as px
from utils import load_project_data

st.set_page_config(layout="wide")
st.title("Investigative Insights & Contractor Networks")
st.markdown("This page connects project data to findings from the policy note on contract concentration.")

df = load_project_data()

if df is not None:
    st.info("Analysis based on the Senate Blue Ribbon Investigation and the 'Sumbong sa Pangulo' portal.")

    contractors_of_interest = [
        'LEGACY CONSTRUCTION', 'AL-JANA CONSTRUCTION', 'L.L.M. CONSTRUCTION',
        'R.D. INTERIOR JUNIOR CONSTRUCTION', 'ST. GERRARD CONSTRUCTION', 
        'IBAYO CONSTRUCTION', 'A.M.S. GONZALES', 'B.M.D. CONSTRUCTION', 'R.D. DISCAYA'
    ]
    
    interest_df = df[df['Contractor'].str.contains('|'.join(contractors_of_interest), case=False, na=False)]

    st.subheader("Visualizing Contract Concentration")
    st.markdown("The treemap below illustrates the distribution of contract values among key contractors identified in the policy note and related inquiries.")
    treemap_data = interest_df.groupby('Contractor')['ContractCost'].sum().reset_index()

    fig = px.treemap(treemap_data, path=[px.Constant("All Contractors"), 'Contractor'], values='ContractCost', color='ContractCost', color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Summary for Identified Contractors")
        summary_df = interest_df.groupby('Contractor').agg(
            Total_Contract_Value=('ContractCost', 'sum'),
            Number_of_Projects=('Contractor', 'count')
        ).sort_values(by='Total_Contract_Value', ascending=False)
        st.dataframe(summary_df.style.format({'Total_Contract_Value': '₱{:,.2f}'}))
    with col2:
        st.subheader("Policy Note Conclusion")
        st.warning("The analysis reveals...a high concentration of contracts among a network of interconnected firms...underscoring the necessity for continued oversight.")
    
    st.subheader("Further Reading")
    st.markdown("- [Inquirer.net: Senate blue ribbon panel seeks lookout bulletin...](https://globalnation.inquirer.net/290127/senate-blue-ribbon-panel-seeks-lookout-bulletin-vs-contractors-dpwh-officials)")
    st.markdown("- [Politiko: Discaya admits owning 9 firms...](https://politiko.com.ph/2025/09/01/umamin-din-discaya-admits-owning-9-firms-that-bagged-flood-control-deals/politiko-lokal/)")
