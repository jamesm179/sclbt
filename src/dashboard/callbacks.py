import logging
from dash import Output, Input, State, callback_context, html, dcc, no_update
from datetime import datetime
import dash_bootstrap_components as dbc
import pandas as pd
from src.config.config_manager import config_manager

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
        # This is still a simplified version of the final callback
        last_update = datetime.now().strftime('%H:%M:%S')
        status_text = "Connected"
        bot_status_card = html.Div([html.P(f"Active Trades: {len(bot.engine.active_trades)}")])
        performance_card = html.Div([html.P(f"Balance: ${bot.engine.balance:,.2f}")])
        api_status_card = html.Div([html.P("API Health: Good")])
        technicals_table = create_table(pd.DataFrame(bot.display.create_technical_data()))
        trades_table = create_table(pd.DataFrame(bot.display.create_trade_data()))
        return (last_update, status_text, bot_status_card, performance_card,
                api_status_card, technicals_table, trades_table)

    # --- Settings Callbacks ---
    @app.callback(Output("settings-offcanvas", "is_open"), Input("open-settings-button", "n_clicks"), State("settings-offcanvas", "is_open"))
    def toggle_offcanvas(n1, is_open):
        if n1: return not is_open
        return is_open

    @app.callback(
        [Output("settings-content", "style"), Output("settings-password-section", "style")],
        Input("unlock-settings-button", "n_clicks"),
        State("settings-password-input", "value"),
        prevent_initial_call=True
    )
    def verify_password(n_clicks, password):
        if password == "admin123": return {"display": "block"}, {"display": "none"}
        return {"display": "none"}, {"display": "block"}

    @app.callback(
        Output("strategy-parameters-display", "children"),
        Input("strategy-checklist", "value")
    )
    def update_strategy_parameters_display(selected_strategies):
        if not selected_strategies:
            return "Select a strategy to see its parameters."

        all_params = config_manager.get('strategies', {})
        inputs = []
        for strat_name in selected_strategies:
            inputs.append(html.H6(strat_name, className="mt-3"))
            strat_params = all_params.get(strat_name, {})
            for key, value in strat_params.items():
                inputs.append(html.Div([
                    html.Label(key, style={"margin-right": "10px"}),
                    dcc.Input(
                        id={'type': 'strategy-param', 'strat': strat_name, 'param': key},
                        type='number' if isinstance(value, (int, float)) else 'text',
                        value=value,
                        className="w-50"
                    )
                ]))
        return inputs

    @app.callback(
        Output("settings-saved-message", "children"),
        Input("apply-settings-button", "n_clicks"),
        State({'type': 'strategy-param', 'strat': ALL, 'param': ALL}, 'value'),
        State({'type': 'strategy-param', 'strat': ALL, 'param': ALL}, 'id'),
        # Add all other settings inputs as State
        prevent_initial_call=True
    )
    def apply_settings(n_clicks, param_values, param_ids):
        if not n_clicks: return no_update

        # Update strategy params
        updated_strategies = config_manager.get('strategies', {})
        for i, param_id in enumerate(param_ids):
            strat_name = param_id['strat']
            param_name = param_id['param']
            updated_strategies[strat_name][param_name] = param_values[i]
        config_manager.set('strategies', updated_strategies)

        # Update other settings...

        bot.display.add_log("Settings applied successfully.")
        return "Settings Saved!"

    pass
