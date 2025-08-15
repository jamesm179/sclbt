import logging
from dash import Output, Input, State, callback_context, html, dcc
from datetime import datetime
import dash_bootstrap_components as dbc
import pandas as pd
from src.config.config_manager import config_manager

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
        # This function will be responsible for fetching all data from the bot
        # and formatting it for the dashboard. For now, it returns placeholders.

        last_update = datetime.now().strftime('%H:%M:%S')
        status_text = "Connected"

        # Placeholder data
        bot_status_card = [html.P("Total Pairs: 0"), html.P("Active Trades: 0")]
        performance_card = [html.P("Balance: $1000.00"), html.P("Signals Today: 0")]
        api_status_card = [html.P("API Health: Good"), html.P("Connectivity: Normal")]

        technicals_table = dbc.Table.from_dataframe(pd.DataFrame({"Pair": ["N/A"], "Signal": ["N/A"]}))
        trades_table = dbc.Table.from_dataframe(pd.DataFrame({"Pair": ["No active trades"], "P/L%": ["-"]}))
        candles_table = dbc.Table.from_dataframe(pd.DataFrame({"Pair": ["N/A"], "Close": ["N/A"]}))

        logs = "\n".join(bot.display.log_messages if hasattr(bot.display, 'log_messages') else ["No logs yet."])

        return (last_update, status_text, bot_status_card, performance_card,
                api_status_card, technicals_table, trades_table, candles_table, logs)

    # --- Settings Callbacks ---
    @app.callback(
        Output("settings-offcanvas", "is_open"),
        Input("open-settings-button", "n_clicks"),
        State("settings-offcanvas", "is_open"),
    )
    def toggle_settings_offcanvas(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        [
            Output("settings-content", "style"),
            Output("settings-password-section", "style"),
            Output("password-error-message", "children"),
            Output("password-verified-store", "data")
        ],
        Input("unlock-settings-button", "n_clicks"),
        [
            State("settings-password-input", "value"),
            State("password-verified-store", "data")
        ],
        prevent_initial_call=True
    )
    def verify_settings_password(n_clicks, password, is_verified):
        if is_verified:
            return {"display": "block"}, {"display": "none"}, "", True

        if n_clicks:
            # In a real app, this should be a securely hashed password
            if password == "admin123":
                return {"display": "block"}, {"display": "none"}, "", True
            else:
                return {"display": "none"}, {"display": "block"}, "Incorrect password", False
        return dash.no_update

    @app.callback(
        Output("settings-saved-message", "children"),
        Input("apply-strategy-button", "n_clicks"),
        [
            State("auto-trading-toggle", "value"),
            State("strategy-checklist", "value"),
            State("leverage-slider", "value"),
            # Add states for all other settings inputs here
        ],
        prevent_initial_call=True
    )
    def apply_all_settings(n_clicks, auto_trading_val, strategies_val, leverage_val):
        if not n_clicks:
            return ""

        ctx = callback_context
        if not ctx.triggered:
            return ""

        try:
            # Save all settings to the config manager
            config_manager.set("auto_trading", "auto" in (auto_trading_val or []))
            config_manager.set("active_strategies", strategies_val or [])
            config_manager.set("leverage", leverage_val)

            # Here you would get and set all other strategy parameters

            logging.info("Settings have been updated and saved.")
            bot.display.add_log("Settings saved successfully.")
            return "Settings Saved!"
        except Exception as e:
            logging.error(f"Error applying settings: {e}")
            return f"Error: {e}"

    # Add other callbacks for manual trading, kill switch, etc. here later.
    pass
