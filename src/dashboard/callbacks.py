import logging
from dash import Output, Input, State, callback_context, html, dcc, no_update, ALL
from datetime import datetime
import dash_bootstrap_components as dbc
import pandas as pd
from src.config.config_manager import config_manager
import asyncio

def create_table(df):
    if df.empty: return dbc.Alert("No data available.", color="info", className="mt-2")
    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True, className="table-sm")

def register_callbacks(app, bot):

    # --- Main Dashboard Refresh Callback ---
    @app.callback(
        [
            Output('last-update-time', 'children'), Output('status-indicator', 'children'),
            Output('bot-status-card', 'children'), Output('performance-card', 'children'),
            Output('api-status-card', 'children'), Output('technicals-table', 'children'),
            Output('trades-table', 'children'), Output('candles-table', 'children'),
            Output('log-container', 'children')
        ],
        Input('refresh-interval', 'n_intervals')
    )
    def update_dashboard(n):
        try:
            # --- Fetch Data ---
            active_trades_list = bot.display.create_trade_data()
            technicals_list = bot.display.create_technical_data()
            candles_list = bot.display.create_candles_data()
            logs = "\n".join(bot.display.log_messages or ["No logs yet."])

            # --- Format Components ---
            bot_status_card = html.Div([html.P(f"Active Trades: {len(active_trades_list)}")])
            performance_card = html.Div([html.P(f"Balance: ${bot.engine.balance:,.2f}")])
            api_status_card = html.Div([html.P("API Health: Good")])

            technicals_table = create_table(pd.DataFrame(technicals_list))
            trades_table = create_table(pd.DataFrame(active_trades_list)) if active_trades_list else "No active trades."
            candles_table = create_table(pd.DataFrame(candles_list))

            return (datetime.now().strftime('%H:%M:%S'), "Connected", bot_status_card, performance_card,
                    api_status_card, technicals_table, trades_table, candles_table, logs)
        except Exception as e:
            logging.error(f"Error updating dashboard: {e}", exc_info=True)
            error_msg = "Error updating dashboard. Check logs."
            return (error_msg, "Error", [], [], [], error_msg, error_msg, error_msg, str(e))

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

        history_table = create_table(filtered_df)
        return history_table, pair_options, strategy_options

    @app.callback(
        Output("settings-saved-message", "children"),
        Input("apply-settings-button", "n_clicks"),
        [
            State("positive-color-input", "value"),
            State("negative-color-input", "value"),
            State("neutral-color-input", "value"),
            # Add other states here
        ],
        prevent_initial_call=True
    )
    def apply_settings(n_clicks, pos_color, neg_color, neut_color):
        if not n_clicks:
            return no_update

        colors = {
            "positive": pos_color,
            "negative": neg_color,
            "neutral": neut_color
        }
        config_manager.set('colors', colors)

        # Logic to save other settings would go here

        bot.display.add_log("Settings applied successfully.")
        return "Settings Saved!"

    # --- Timeframe Selector Callback ---
    @app.callback(
        Output('timeframe-store', 'data'), # Dummy output
        Input('timeframe-selector', 'value'),
        prevent_initial_call=True
    )
    def update_timeframe(selected_timeframe):
        if not selected_timeframe:
            return no_update

        config_manager.set('timeframe', selected_timeframe)
        bot.display.add_log(f"Timeframe changed to: {selected_timeframe}")
        return selected_timeframe

    # Other callbacks...
    pass
