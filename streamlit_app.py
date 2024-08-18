import streamlit as st
import pandas as pd
import plotly.express as px
import requests


def fetch_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from DeFi Llama: {e}")
        return None


def fetch_historical_data(pool_id):
    url = f"https://yields.llama.fi/chart/{pool_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching historical data for pool {pool_id}: {e}")
        return None


# API Endpoints
PROTOCOLS_API_URL = "https://api.llama.fi/protocols"
CHAINS_API_URL = "https://api.llama.fi/chains"
TVL_BY_CATEGORY_API_URL = "https://api.llama.fi/charts"


def load_data():
    chains_data = fetch_data(CHAINS_API_URL)
    protocols_data = fetch_data(PROTOCOLS_API_URL)
    yields_data = fetch_data("https://yields.llama.fi/pools")

    if chains_data:
        chains_df = pd.DataFrame(chains_data)
        chains_df['tvl'] = pd.to_numeric(chains_df['tvl'], errors='coerce').fillna(0)
        st.session_state['chains_df'] = chains_df

    if protocols_data:
        protocols_df = pd.DataFrame(protocols_data)
        protocols_df['tvl'] = pd.to_numeric(protocols_df['tvl'], errors='coerce').fillna(0)
        st.session_state['protocols_df'] = protocols_df

    if yields_data:
        yields_df = pd.DataFrame(yields_data)
        st.session_state['yields_df'] = yields_df


def overview_page():
    st.title("DEX Tracker Overview")

    if 'chains_df' in st.session_state:
        chains_df = st.session_state.chains_df

        total_tvl = chains_df['tvl'].sum()
        st.metric("Total Value Locked (All Chains)", f"${total_tvl:,.2f}")

        num_chains = len(chains_df)
        st.metric("Number of Chains", num_chains)

        top_chains = chains_df.nlargest(10, 'tvl')
        st.subheader("Top 10 Chains by TVL")
        st.table(top_chains[['name', 'tvl']])

        fig_bar = px.bar(
            top_chains,
            x='tvl',
            y='name',
            orientation='h',
            title='Top 10 Chains by TVL',
            labels={'tvl': 'Total Value Locked (USD)', 'name': 'Chain'},
        )
        fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
        fig_bar.update_traces(
            texttemplate='%{x:.2s}', textposition='outside',
            hovertemplate='<b>%{y}</b><br>Total Value Locked: %{x:,.2f}<extra></extra>'
        )
        st.plotly_chart(fig_bar)

        fig_sunburst = px.sunburst(
            chains_df,
            path=['name'],
            values='tvl',
            title='TVL Distribution by Chain'
        )
        st.plotly_chart(fig_sunburst)


def chains_page():
    st.title("TVL by Chain")

    if 'chains_df' in st.session_state:
        chains_df = st.session_state.chains_df.copy()
        chains_df['tvl'] = pd.to_numeric(chains_df['tvl'], errors='coerce').fillna(0)
        chains_df = chains_df.sort_values(by='tvl', ascending=False)

        fig = px.bar(
            chains_df,
            x='name',
            y='tvl',
            title='Total Value Locked (TVL) by Chain',
            labels={'tvl': 'Total Value Locked (USD)', 'name': 'Chain'},
        )
        fig.update_layout(xaxis_title="Chain", yaxis_title="Total Value Locked (USD)")
        fig.update_traces(
            texttemplate='%{y:,.2f}', textposition='outside',
            hovertemplate='<b>%{x}</b><br>Total Value Locked: %{y:,.2f}<extra></extra>'
        )
        st.plotly_chart(fig)


def protocols_page():
    st.title("TVL by Protocol")

    if 'protocols_df' in st.session_state:
        protocols_df = st.session_state.protocols_df.copy()
        protocols_df['tvl'] = pd.to_numeric(protocols_df['tvl'], errors='coerce').fillna(0)
        protocols_df = protocols_df.sort_values(by='tvl', ascending=False)

        fig = px.bar(
            protocols_df,
            x='name',
            y='tvl',
            title='Total Value Locked (TVL) by Protocol',
            labels={'tvl': 'Total Value Locked (USD)', 'name': 'Protocol'},
        )
        fig.update_layout(xaxis_title="Protocol", yaxis_title="Total Value Locked (USD)")
        fig.update_traces(
            texttemplate='%{y:,.2f}', textposition='outside',
            hovertemplate='<b>%{x}</b><br>Total Value Locked: %{y:,.2f}<extra></extra>'
        )
        st.plotly_chart(fig)


def yields_page():
    st.title("DeFi Yields")

    if 'yields_df' in st.session_state:
        yields_df = st.session_state.yields_df

        # Display the available coins
        coins = yields_df['symbol'].unique()
        selected_coin = st.selectbox("Select Coin", options=coins)

        # Filter yields data based on selected coin
        filtered_yields_df = yields_df[yields_df['symbol'] == selected_coin]

        st.subheader(f"Yields for {selected_coin}")

        if not filtered_yields_df.empty:
            st.table(filtered_yields_df[['chain', 'project', 'tvlUsd', 'apyBase', 'apy']])

            # Plot yield distribution
            fig = px.bar(
                filtered_yields_df,
                x='chain',
                y='apyBase',
                title=f'APY Base Distribution for {selected_coin}',
                labels={'apyBase': 'APY Base (%)', 'chain': 'Chain'}
            )
            fig.update_layout(xaxis_title='Chain', yaxis_title='APY Base (%)')
            st.plotly_chart(fig)
        else:
            st.write(f"No data available for {selected_coin}")


def tvl_by_category_page():
    st.title("TVL by Category")

    if 'tvl_by_category_df' in st.session_state:
        tvl_by_category_df = st.session_state.tvl_by_category_df

        # Inspect the data
        st.write(tvl_by_category_df)
        st.write(type(tvl_by_category_df))

        # Display the total TVL if available
        if isinstance(tvl_by_category_df, list) and len(tvl_by_category_df) > 0:
            df = pd.DataFrame(tvl_by_category_df)
            st.write(df.head())

            # Check if 'totalTvl' or similar column exists
            if 'totalTvl' in df.columns:
                total_tvl = df['totalTvl'].sum()
                st.metric("Total TVL by Category", f"${total_tvl:,.2f}")

            # Plot TVL by category
            fig = px.bar(
                df,
                x='category',
                y='tvl',
                title='TVL by Category',
                labels={'tvl': 'Total Value Locked (USD)', 'category': 'Category'},
            )
            st.plotly_chart(fig)


def historical_data_page():
    st.title("Historical APY and TVL Data")

    if 'yields_df' in st.session_state:
        yields_df = st.session_state.yields_df

        # Display the available pools
        pools = yields_df['pool'].unique()
        selected_pool = st.selectbox("Select Pool", options=pools)

        # Fetch historical data for the selected pool
        historical_data = fetch_historical_data(selected_pool)

        if historical_data:
            historical_df = pd.DataFrame(historical_data['data'])
            historical_df['timestamp'] = pd.to_datetime(historical_df['timestamp'])
            historical_df.set_index('timestamp', inplace=True)

            st.subheader(f"Historical Data for Pool {selected_pool}")

            # Display the historical data
            st.line_chart(historical_df[['tvlUsd', 'apy']], use_container_width=True)

            # Plot APY and TVL over time
            fig = px.line(
                historical_df,
                x=historical_df.index,
                y=['tvlUsd', 'apy'],
                labels={'value': 'Amount', 'variable': 'Metric'},
                title=f'Historical TVL and APY for Pool {selected_pool}'
            )
            st.plotly_chart(fig)


# Main page navigation
def main():
    st.sidebar.title("Navigation")
    options = ["Overview", "Chains", "Protocols"]
    choice = st.sidebar.selectbox("Select a page", options)

    if choice == "Overview":
        overview_page()
    elif choice == "Chains":
        chains_page()
    elif choice == "Protocols":
        protocols_page()


if __name__ == "__main__":
    load_data()
    main()
