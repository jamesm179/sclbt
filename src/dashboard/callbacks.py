import logging
from dash import Output, Input, State, callback_context, html, dcc, no_update
from datetime import datetime
import dash_bootstrap_components as dbc
import pandas as pd
from src.config.config_manager import config_manager

def create_table(df):
    """Helper function to create a dbc.Table from a DataFrame."""
    if df.empty:
        return "No data available."
    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True, className="table-sm")

def register_callbacks(app, bot):

    # --- Main Dashboard Refresh Callback ---
    @app.callback(
        [
            Output('last-update-time', 'children'),
            Output('status-indicator', 'children'),
            Output('bot-status-card', 'children'),
            Output('performance-card', 'children'),
            Output('api-status-card', 'children'),
            Output('technicals-table', 'children'),
            Output('trades-table', 'children'),
            Output('candles-table', 'children'),
            Output('log-container', 'children'),
        ],
        Input('refresh-interval', 'n_intervals')
    )
    def update_dashboard(n):
        try:
            last_update = datetime.now().strftime('%H:%M:%S')
            status_text = "Connected"

            # --- Fetch Data ---
            active_trades_list = bot.display.create_trade_data()
            technicals_list = bot.display.create_technical_data()
            candles_list = bot.display.create_candles_data()
            logs = "\n".join(bot.display.log_messages or ["No logs yet."])

            # --- Format Components ---
            bot_status_card = html.Div([
                html.P(f"Total Pairs: {len(bot.pairs)}"),
                html.P(f"Active Trades: {len(active_trades_list)}")
            ])

            performance_card = html.Div([
                html.P(f"Balance: ${bot.engine.balance:,.2f}"),
                html.P(f"Signals Today: {bot.engine.signals_today}")
            ])

            api_status_card = html.Div([
                html.P("API Health: Good"), # Placeholder
                html.P(f"Connectivity: {bot.connectivity_monitor.current_status}")
            ])

            # --- Create Tables ---
            technicals_table = create_table(pd.DataFrame(technicals_list))
            trades_table = create_table(pd.DataFrame(active_trades_list)) if active_trades_list else "No active trades."
            candles_table = create_table(pd.DataFrame(candles_list))

            return (last_update, status_text, bot_status_card, performance_card,
                    api_status_card, technicals_table, trades_table, candles_table, logs)

        except Exception as e:
            logging.error(f"Error updating dashboard: {e}", exc_info=True)
            error_message = "Error updating dashboard. Check logs."
            return (error_message, "Error", [], [], [], error_message, error_message, error_message, str(e))

    # --- Settings Callbacks ---
    @app.callback(
        Output("settings-offcanvas", "is_open"),
        Input("open-settings-button", "n_clicks"),
        State("settings-offcanvas", "is_open"),
    )
    def toggle_offcanvas(n_clicks, is_open):
        if n_clicks: return not is_open
        return is_open

    # Other callbacks remain the same...
    pass
