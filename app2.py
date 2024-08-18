import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Replace with your actual API key
API_KEY = 'BqzlxBHFCXvRcsyOpuewEH8wMl9V8jul'
BASE_URL = 'https://api.dune.com/api/v1'

# Define your queries
STAKING_REWARDS_QUERY_ID = 'your_sol_staking_rewards_query_id'
FEES_PAID_QUERY_ID = 'your_l2_to_l1_fees_query_id'

# Function to get results from a query
def get_query_results(query_id):
    url = f"{BASE_URL}/queries/{query_id}/results"
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching data: {response.status_code} - {response.text}")
        return None

# Function to load data into session state
def load_data():
    staking_rewards_data = get_query_results(STAKING_REWARDS_QUERY_ID)
    fees_paid_data = get_query_results(FEES_PAID_QUERY_ID)

    if staking_rewards_data:
        staking_rewards_df = pd.DataFrame(staking_rewards_data['data'])
        st.session_state['staking_rewards_df'] = staking_rewards_df

    if fees_paid_data:
        fees_paid_df = pd.DataFrame(fees_paid_data['data'])
        st.session_state['fees_paid_df'] = fees_paid_df

def staking_rewards_page():
    st.title("Solana Staking Rewards")

    if 'staking_rewards_df' in st.session_state:
        df = st.session_state['staking_rewards_df']

        # Ensure 'timestamp' is in datetime format
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        fig = px.line(
            df,
            x='timestamp',
            y='apy',
            title='Solana Staking Rewards Over Time',
            labels={'timestamp': 'Date', 'apy': 'APY (%)'}
        )
