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

    # Other callbacks...
    pass
