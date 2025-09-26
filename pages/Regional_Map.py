import streamlit as st
import plotly.express as px
from utils import load_project_data, get_geojson

st.set_page_config(layout="wide")
st.title(" Geographic Map of Projects")

df = load_project_data()
geojson = get_geojson()

if df is not None and geojson is not None:
    map_metric = st.sidebar.selectbox("Select Metric", options=['Total Contract Cost', 'Number of Projects'])

    if map_metric == 'Total Contract Cost':
        agg_data = df.groupby('Region_std')['ContractCost'].sum().reset_index()
        color_col = 'ContractCost'
    else:
        agg_data = df.groupby('Region_std').size().reset_index(name='Number of Projects')
        color_col = 'Number of Projects'

    st.subheader(f"Map of {map_metric} by Region")
    fig = px.choropleth_mapbox(
        agg_data, geojson=geojson, locations='Region_std',
        featureidkey="properties.region_name", color=color_col,
        color_continuous_scale="Viridis", mapbox_style="carto-positron",
        zoom=4.5, center = {"lat": 12.8797, "lon": 121.7740}, opacity=0.6,
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(agg_data.sort_values(by=color_col, ascending=False))
