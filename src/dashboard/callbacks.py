import logging
from dash import Output, Input, State, callback_context, html, dcc, no_update, ALL
from datetime import datetime
import dash_bootstrap_components as dbc
import pandas as pd
from src.config.config_manager import config_manager
import asyncio

def create_table(df):
    if df.empty: return "No data available."
    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True, className="table-sm")

def register_callbacks(app, bot):

    # --- Main Dashboard Refresh Callback ---
    @app.callback(
        [Output(x, 'children') for x in ['last-update-time', 'status-indicator', 'bot-status-card',
                                         'performance-card', 'api-status-card', 'technicals-table',
                                         'trades-table']],
        Input('refresh-interval', 'n_intervals')
    )
    def update_dashboard(n):
        # ... (implementation from before)
        return ["-"]*7 # Placeholder

    # --- Multi-Timeframe Analysis Callback ---
    @app.callback(
        [Output('market-sentiment-card', 'children'),
         Output('multi-timeframe-table', 'children'),
         Output('mtf-pair-selector', 'options'),
         Output('mtf-pair-selector', 'value')],
        [Input('refresh-interval', 'n_intervals'),
         Input('mtf-pair-selector', 'value')]
    )
    def update_mtf_analysis(n, selected_pair):
        # 1. Get available pairs for dropdown
        all_pairs = config_manager.get('manual_trading_pairs', [])
        pair_options = [{'label': p, 'value': p.replace('/', '_')} for p in all_pairs]

        # 2. If no pair is selected, choose the first one
        if not selected_pair and all_pairs:
            selected_pair = all_pairs[0].replace('/', '_')

        if not selected_pair:
            return "Select a pair", "No data", pair_options, None

        # 3. Fetch and process data for multiple timeframes (async)
        async def fetch_and_process():
            timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
            tasks = [bot.process_pair(bot.api_clients['coindcx'], {'symbol': selected_pair}, tf) for tf in timeframes]
            results = await asyncio.gather(*tasks)
            return results

        # This is a simplified way to run the async code
        try:
            loop = asyncio.get_running_loop()
            tf_data = loop.create_task(fetch_and_process())
        except RuntimeError:
            tf_data = asyncio.run(fetch_and_process())

        # 4. Format the data for display (placeholders for now)
        sentiment_card = html.Div([html.H5("Market Sentiment: NEUTRAL")])

        # This would be a detailed table
        mtf_table = html.Div("Multi-timeframe analysis table placeholder.")

        return sentiment_card, mtf_table, pair_options, selected_pair

    # --- Settings Callbacks ---
    # ... (implementation from before)

    pass

# Helper to run async from sync context if needed
def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
        return loop.create_task(coro)
    except RuntimeError:
        return asyncio.run(coro)
