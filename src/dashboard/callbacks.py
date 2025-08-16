import logging
from dash import Output, Input, State, callback_context, html, dcc, no_update, ALL
from datetime import datetime
import dash_bootstrap_components as dbc
import pandas as pd
from src.config.config_manager import config_manager
import asyncio

# ... (other helper functions and callbacks) ...

def register_callbacks(app, bot):

    # ... (update_dashboard, mtf_analysis, and settings callbacks) ...

    # --- Trade History Callback ---
    @app.callback(
        [Output('trade-history-table', 'children'),
         Output('trade-history-pair-filter', 'options'),
         Output('trade-history-strategy-filter', 'options')],
        [Input('refresh-interval', 'n_intervals'),
         Input('trade-history-pair-filter', 'value'),
         Input('trade-history-strategy-filter', 'value')]
    )
    def update_trade_history(n, pair_filter, strategy_filter):
        history_df = bot.engine.performance_tracker.get_all_trade_history()

        if history_df.empty:
            return "No trade history available.", [], []

        # Populate filter options
        pair_options = [{'label': 'All Pairs', 'value': 'all'}] + [{'label': p, 'value': p} for p in history_df['Pair'].unique()]
        strategy_options = [{'label': 'All Strategies', 'value': 'all'}] + [{'label': s, 'value': s} for s in history_df['Strategy'].unique()]

        # Filter data
        filtered_df = history_df.copy()
        if pair_filter and pair_filter != 'all':
            filtered_df = filtered_df[filtered_df['Pair'] == pair_filter]
        if strategy_filter and strategy_filter != 'all':
            filtered_df = filtered_df[filtered_df['Strategy'] == strategy_filter]

        # Create table
        history_table = create_table(filtered_df)

        return history_table, pair_options, strategy_options

    pass
