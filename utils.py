import streamlit as st
import pandas as pd
import numpy as np
import requests

@st.cache_data
def load_project_data():
    """Loads and processes the main flood control project data."""
    file_path = 'data/Flood_Control_Data.csv'
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found.")
        return None

    # Data Cleaning
    date_columns = ['CompletionDateActual', 'StartDate', 'CompletionDateOriginal']
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    currency_columns = ['ApprovedBudgetForTheContract', 'ContractCost']
    for col in currency_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df.dropna(subset=date_columns + currency_columns + ['Contractor', 'Region'], inplace=True)
    
    # Feature Engineering
    df['ProjectDelay'] = (df['CompletionDateActual'] - df['CompletionDateOriginal']).dt.days
    df['BudgetVsCostDifference'] = df['ApprovedBudgetForTheContract'] - df['ContractCost']
    df['BudgetVsCostPercentage'] = np.where(
        df['ApprovedBudgetForTheContract'] > 0,
        (df['BudgetVsCostDifference'] / df['ApprovedBudgetForTheContract']) * 100, 0
    )
    df['Contractor'] = df['Contractor'].str.strip().str.upper().str.replace(r'\(.*\)', '', regex=True)
    
    # Standardize Region Names for mapping
    region_mapping = {
        'REGION I': 'Region I (Ilocos Region)', 'REGION II': 'Region II (Cagayan Valley)',
        'REGION III': 'Region III (Central Luzon)', 'REGION IV-A': 'Region IV-A (CALABARZON)',
        'REGION IV-B': 'Region IV-B (MIMAROPA)', 'REGION V': 'Region V (Bicol Region)',
        'REGION VI': 'Region VI (Western Visayas)', 'REGION VII': 'Region VII (Central Visayas)',
        'REGION VIII': 'Region VIII (Eastern Visayas)', 'REGION IX': 'Region IX (Zamboanga Peninsula)',
        'REGION X': 'Region X (Northern Mindanao)', 'REGION XI': 'Region XI (Davao Region)',
        'REGION XII': 'Region XII (SOCCSKSARGEN)', 'REGION XIII': 'Region XIII (Caraga)',
        'CAR': 'Cordillera Administrative Region (CAR)', 'NCR': 'National Capital Region (NCR)',
        'BARMM': 'Bangsamoro Autonomous Region in Muslim Mindanao (BARMM)'
    }
    df['Region_std'] = df['Region'].str.upper().str.strip().replace(region_mapping)

    return df

@st.cache_data
def get_geojson():
    """Fetches and caches the GeoJSON for PH regions."""
    url = "https://raw.githubusercontent.com/gjevel/philippines-geojson/master/regions/ph-regions-no-islands.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch GeoJSON from URL: {e}")
        return None
