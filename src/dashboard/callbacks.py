import logging
from dash import Output, Input, State, callback_context, html, dcc, no_update, ALL
from datetime import datetime
import dash_bootstrap_components as dbc
import pandas as pd
from src.config.config_manager import config_manager

def create_table_from_dataframe(df):
    """Helper function to create a dbc.Table from a DataFrame."""
    if df.empty:
        return dbc.Alert("No data available.", color="info")
    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True, className="table-sm")

def register_callbacks(app, bot):

    # --- Main Dashboard Refresh Callback ---
    @app.callback(
        [Output('last-update-time', 'children'), Output('status-indicator', 'children'),
         Output('bot-status-card', 'children'), Output('performance-card', 'children'),
         Output('api-status-card', 'children'), Output('technicals-table', 'children'),
         Output('trades-table', 'children')],
        Input('refresh-interval', 'n_intervals')
    )
    def update_dashboard(n):
        # This is still a simplified version for now
        last_update = datetime.now().strftime('%H:%M:%S')
        status_text = "Connected"
        bot_status_card = html.Div([html.P(f"Active Trades: {len(bot.engine.active_trades)}")])
        performance_card = html.Div([html.P(f"Balance: ${bot.engine.balance:,.2f}")])
        api_status_card = html.Div([html.P("API Health: Good")])
        technicals_table = create_table_from_dataframe(pd.DataFrame(bot.display.create_technical_data()))
        trades_table = create_table_from_dataframe(pd.DataFrame(bot.display.create_trade_data()))
        return (last_update, status_text, bot_status_card, performance_card, api_status_card, technicals_table, trades_table)

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

        pair_options = [{'label': 'All', 'value': 'all'}] + [{'label': p, 'value': p} for p in history_df['Pair'].unique()]
        strategy_options = [{'label': 'All', 'value': 'all'}] + [{'label': s, 'value': s} for s in history_df['Strategy'].unique()]

        filtered_df = history_df.copy()
        if pair_filter and pair_filter != 'all':
            filtered_df = filtered_df[filtered_df['Pair'] == pair_filter]
        if strategy_filter and strategy_filter != 'all':
            filtered_df = filtered_df[filtered_df['Strategy'] == strategy_filter]

        history_table = create_table_from_dataframe(filtered_df)
        return history_table, pair_options, strategy_options

    # Other callbacks...
    pass
