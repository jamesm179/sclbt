import logging
from dash import Output, Input, State, callback_context, html, dcc, no_update
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
        # This function fetches data from the bot and formats it for the dashboard.
        # This is a simplified version. A full implementation would be much more complex.

        try:
            last_update = datetime.now().strftime('%H:%M:%S')
            status_text = "Connected"

            # --- Fetch Data ---
            active_trades = bot.engine.active_trades or {}
            active_trades_count = len(active_trades)
            balance = bot.engine.balance
            signals_today = bot.engine.signals_today

            # --- Format Components ---
            bot_status_card = html.Div([
                html.P(f"Total Pairs: {len(bot.pairs)}"),
                html.P(f"Active Trades: {active_trades_count}")
            ])

            performance_card = html.Div([
                html.P(f"Balance: ${balance:,.2f}"),
                html.P(f"Signals Today: {signals_today}")
            ])

            api_status_card = html.Div([
                html.P(f"API Health: Good"),
                html.P(f"Connectivity: {bot.connectivity_monitor.current_status}")
            ])

            # In a real implementation, data for tables would be generated here
            technicals_table = html.Div("Technical data placeholder.")
            trades_table = html.Div(f"{active_trades_count} active trades.")
            candles_table = html.Div("Candle data placeholder.")

            logs = "\n".join(bot.display.log_messages or ["No logs yet."])

            return (last_update, status_text, bot_status_card, performance_card,
                    api_status_card, technicals_table, trades_table, candles_table, logs)
        except Exception as e:
            logging.error(f"Error updating dashboard: {e}", exc_info=True)
            return ["Error"] * 10

    # --- Settings Callbacks ---
    @app.callback(
        Output("settings-offcanvas", "is_open"),
        Input("open-settings-button", "n_clicks"),
        State("settings-offcanvas", "is_open"),
    )
    def toggle_offcanvas(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        [Output("settings-content", "style"), Output("settings-password-section", "style")],
        Input("unlock-settings-button", "n_clicks"),
        State("settings-password-input", "value"),
        prevent_initial_call=True
    )
    def verify_password(n_clicks, password):
        if password == "admin123": # Use a secure method in a real app
            return {"display": "block"}, {"display": "none"}
        return {"display": "none"}, {"display": "block"}

    @app.callback(
        Output("settings-saved-message", "children"),
        Input("apply-strategy-button", "n_clicks"),
        [State(component_id, component_property) for component_id, component_property in [
            ("auto-trading-toggle", "value"),
            ("strategy-checklist", "value"),
            ("leverage-slider", "value"),
        ]],
        prevent_initial_call=True
    )
    def apply_settings(n_clicks, auto_trading, active_strategies, leverage):
        if not n_clicks:
            return no_update

        config_manager.set("auto_trading", "auto" in (auto_trading or []))
        config_manager.set("active_strategies", active_strategies or [])
        config_manager.set("leverage", leverage)

        bot.display.add_log("Settings applied successfully.")
        return "Settings Saved!"

    # --- Kill Switch Callbacks ---
    @app.callback(
        Output("kill-switch-modal", "is_open"),
        [Input("emergency-kill-switch-button", "n_clicks"), Input("kill-switch-close-button", "n_clicks")],
        State("kill-switch-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_kill_switch_modal(n_open, n_close, is_open):
        if n_open or n_close:
            return not is_open
        return is_open

    # Placeholder for other callbacks
    pass
