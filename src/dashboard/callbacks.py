import logging
from dash import Output, Input, State, callback_context, html, dcc, no_update, ALL
from datetime import datetime
import dash_bootstrap_components as dbc
import pandas as pd
from src.config.config_manager import config_manager

def create_technicals_table(technicals_data):
    if not technicals_data:
        return dbc.Alert("No technical data available.", color="info")
    header = [html.Thead(html.Tr([
        html.Th("Pair"), html.Th("Exchange"), html.Th("Price"),
        html.Th("Filter"), html.Th("Up/Down"), html.Th("Condition"), html.Th("Signal")
    ]))]
    body = [html.Tbody([
        html.Tr([
            html.Td(tech['pair']), html.Td(tech['exchange']), html.Td(tech['price']),
            html.Td(tech['filt'], style={'color': tech['filt_color']}),
            html.Td(tech['up_down'], style={'color': tech['trend_color']}),
            html.Td(tech['cond'], style={'color': tech['cond_color']}),
            html.Td(tech['signal'], style={'color': tech['signal_color']}),
        ]) for tech in technicals_data
    ])]
    return dbc.Table(header + body, bordered=True, hover=True, responsive=True, striped=True, className="table-sm")

def create_simple_table(df):
    if df.empty: return dbc.Alert("No data available.", color="info")
    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True, className="table-sm")

def register_callbacks(app, bot):
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
            active_trades = bot.display.create_trade_data()
            candles = bot.display.create_candles_data()
            logs = "\n".join(bot.display.log_messages or ["No logs yet."])

            bot_status_card = html.Div([html.P(f"Active Trades: {len(active_trades)}")])
            performance_card = html.Div([html.P(f"Balance: ${bot.engine.balance:,.2f}")])
            api_status_card = html.Div([html.P("API Health: Good")])

            technicals_table = create_technicals_table(bot.display.create_technical_data())
            trades_table = create_simple_table(pd.DataFrame(active_trades))
            candles_table = create_simple_table(pd.DataFrame(candles))

            return (datetime.now().strftime('%H:%M:%S'), "Connected", bot_status_card, performance_card,
                    api_status_card, technicals_table, trades_table, candles_table, logs)
        except Exception as e:
            logging.error(f"Error updating dashboard: {e}", exc_info=True)
            error_msg = "Error updating dashboard. Check logs."
            return (error_msg, "Error", [], [], [], error_msg, error_msg, error_msg, str(e))

    # ... other callbacks
    pass
