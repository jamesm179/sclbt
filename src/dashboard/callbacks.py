from dash import Output, Input, State, callback_context
from datetime import datetime
import logging
from src.config.config_manager import config_manager

def register_callbacks(app, bot):

    # --- Settings Panel Callbacks ---

    @app.callback(
        Output("settings-offcanvas", "is_open"),
        Input("open-settings-button", "n_clicks"),
        State("settings-offcanvas", "is_open"),
    )
    def toggle_offcanvas(n1, is_open):
        if n1:
            return not is_open
        return is_open

    @app.callback(
        Output("settings-content", "style"),
        Output("settings-password-section", "style"),
        Output("password-error-message", "children"),
        Input("unlock-settings-button", "n_clicks"),
        State("settings-password-input", "value"),
        prevent_initial_call=True
    )
    def verify_password(n_clicks, password):
        # In a real app, use a more secure password check
        if password == "admin123":
            return {"display": "block"}, {"display": "none"}, ""
        else:
            return {"display": "none"}, {"display": "block"}, "Incorrect password"

    @app.callback(
        Output("active-strategies-store", "data"), # This is a dummy output, real update happens in bot
        Input("apply-strategy-button", "n_clicks"),
        [
            State("strategy-checklist", "value"),
            State("auto-trading-toggle", "value"),
            State("leverage-slider", "value"),
            # ... other state inputs for all strategy params
        ],
        prevent_initial_call=True
    )
    def apply_settings(n_clicks, active_strategies, auto_trading, leverage):
        if n_clicks:
            logging.info("Apply settings button clicked.")

            # Update active strategies
            config_manager.set('active_strategies', active_strategies)

            # Update auto trading
            config_manager.set('auto_trading', 'auto' in (auto_trading or []))

            # Update leverage
            config_manager.set('leverage', leverage)

            # Here, you would also get the state of all the individual strategy
            # parameters and update them in the config_manager.

            # The bot's internal logic would then react to these config changes.
            logging.info("Settings applied and saved.")

        return active_strategies # Return value for the dummy output


    # --- Main Dashboard Update Callback ---

    @app.callback(
        Output('header-title', 'children'),
        Output('last-update-time', 'children'),
        # ... all other outputs for the dashboard
        Input('refresh-interval', 'n_intervals')
    )
    def update_dashboard(n):
        # This is the main callback that will fetch data from the bot/engine
        # and update all the components on the dashboard.
        # It will be a large and complex function.

        # For now, just update the header
        header_title = f"SNIPER BOT V1 - Refreshed at {datetime.now().strftime('%H:%M:%S')}"
        last_update = datetime.now().strftime('%H:%M:%S')

        # Placeholder for other outputs
        # return header_title, last_update, ...
        return header_title, last_update
