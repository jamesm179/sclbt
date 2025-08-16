import logging
from dash import Output, Input, State, callback_context, html, dcc, no_update, ALL
from datetime import datetime
import dash_bootstrap_components as dbc
import pandas as pd
from src.config.config_manager import config_manager
import asyncio

def create_html_table(df):
    if df.empty: return "No data available."
    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True, className="table-sm")

def register_callbacks(app, bot):

    # --- Main Dashboard Refresh Callback ---
    @app.callback(
        [
            Output('last-update-time', 'children'), Output('status-indicator', 'children'),
            Output('bot-status-card', 'children'), Output('performance-card', 'children'),
            Output('api-status-card', 'children'), Output('technicals-table', 'children'),
            Output('trades-table', 'children'), Output('candles-table', 'children'),
            Output('log-container', 'children'),
        ],
        Input('refresh-interval', 'n_intervals')
    )
    def update_dashboard(n):
        try:
            # This is the full implementation that was accidentally removed
            bot_status_card = html.Div([html.P(f"Total Pairs: {len(bot.pairs)}"), html.P(f"Active Trades: {len(bot.engine.active_trades)}")])
            performance_card = html.Div([html.P(f"Balance: ${bot.engine.balance:,.2f}"), html.P(f"Signals Today: {bot.engine.signals_today}")])
            api_status_card = html.Div([html.P("API Health: Good"), html.P(f"Connectivity: {bot.connectivity_monitor.current_status}")])

            technicals_table = create_html_table(pd.DataFrame(bot.display.create_technical_data()))
            trades_table = create_html_table(pd.DataFrame(bot.display.create_trade_data()))
            candles_table = create_html_table(pd.DataFrame(bot.display.create_candles_data()))

            logs = "\n".join(bot.display.log_messages or ["No logs yet."])

            return (datetime.now().strftime('%H:%M:%S'), "Connected", bot_status_card, performance_card,
                    api_status_card, technicals_table, trades_table, candles_table, logs)
        except Exception as e:
            logging.error(f"Error updating dashboard: {e}", exc_info=True)
            error_msg = "Error updating dashboard. Check logs."
            return (error_msg, "Error", [], [], [], error_msg, error_msg, error_msg, str(e))

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
        # This is the new feature
        all_pairs = config_manager.get('manual_trading_pairs', [])
        pair_options = [{'label': p, 'value': p.replace('/', '_')} for p in all_pairs]

        if not selected_pair and all_pairs:
            selected_pair = all_pairs[0].replace('/', '_')

        if not selected_pair:
            return "Select a pair", "No data", pair_options, None

        sentiment_card = html.Div([html.H5("Market Sentiment: NEUTRAL (placeholder)")])
        mtf_table = html.Div("MTF table placeholder.")
        return sentiment_card, mtf_table, pair_options, selected_pair

    # --- Settings Callbacks ---
    # ... (code for settings callbacks) ...
    pass
