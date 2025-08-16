import logging
from dash import Output, Input, State, callback_context, html, dcc, no_update
from datetime import datetime
import dash_bootstrap_components as dbc
from src.config.config_manager import config_manager

def create_technicals_table(technicals):
    if not technicals: return "No technical data available."
    return dbc.Table([
        html.Thead(html.Tr([
            html.Th("Pair"), html.Th("Price"), html.Th("Filter"),
            html.Th("Up/Down"), html.Th("Condition"), html.Th("Signal"),
            html.Th("Avg P/L%"), html.Th("Actions")
        ])),
        html.Tbody([
            html.Tr([
                html.Td(tech['pair']), html.Td(tech['price']),
                html.Td(tech['filt'], style={'color': tech['filt_color']}),
                html.Td(tech['up_down'], style={'color': tech['trend_color']}),
                html.Td(tech['cond'], style={'color': tech['cond_color']}),
                html.Td(tech['signal'], style={'color': tech['signal_color']}),
                html.Td(tech['avg_pl'], style={'color': tech['pl_color']}),
                html.Td([
                    dbc.Button("Buy", id={'type': 'buy-button', 'index': tech['pair_symbol']}, color="success", size="sm"),
                    dbc.Button("Sell", id={'type': 'sell-button', 'index': tech['pair_symbol']}, color="danger", size="sm", className="ms-1")
                ])
            ]) for tech in technicals
        ]),
    ], bordered=True, hover=True, responsive=True, striped=True, className="table-sm")

def create_trades_table(trades):
    if not trades: return "No active trades."
    return dbc.Table([
        html.Thead(html.Tr([
            html.Th("Pair"), html.Th("Direction"), html.Th("Entry Price"),
            html.Th("Current"), html.Th("P/L%"), html.Th("SL"), html.Th("TP"),
            html.Th("Action")
        ])),
        html.Tbody([
            html.Tr([
                html.Td(trade['pair']),
                html.Td(trade['direction'], style={'color': trade['dir_color']}),
                html.Td(trade['entry_price']), html.Td(trade['current_price']),
                html.Td(trade['profit_pct'], style={'color': trade['pl_color']}),
                html.Td(trade['stop_loss']), html.Td(trade['take_profit']),
                html.Td(dbc.Button("Exit", id={'type': 'exit-button', 'index': trade['symbol']}, color="warning", size="sm"))
            ]) for trade in trades
        ]),
    ], bordered=True, hover=True, responsive=True, striped=True, className="table-sm")

def create_candles_table(candles):
    if not candles: return "No candle data available."
    return dbc.Table.from_dataframe(pd.DataFrame(candles), striped=True, bordered=True, hover=True, responsive=True, className="table-sm")

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
            bot_status_card = html.Div([html.P(f"Total Pairs: {len(bot.pairs)}"), html.P(f"Active Trades: {len(bot.engine.active_trades)}")])
            performance_card = html.Div([html.P(f"Balance: ${bot.engine.balance:,.2f}"), html.P(f"Signals Today: {bot.engine.signals_today}")])
            api_status_card = html.Div([html.P("API Health: Good"), html.P(f"Connectivity: {bot.connectivity_monitor.current_status}")])

            technicals_table = create_technicals_table(bot.display.create_technical_data())
            trades_table = create_trades_table(bot.display.create_trade_data())
            candles_table = create_candles_table(bot.display.create_candles_data())

            logs = "\n".join(bot.display.log_messages or ["No logs yet."])

            return (datetime.now().strftime('%H:%M:%S'), "Connected", bot_status_card, performance_card,
                    api_status_card, technicals_table, trades_table, candles_table, logs)
        except Exception as e:
            logging.error(f"Error updating dashboard: {e}", exc_info=True)
            error_msg = "Error updating dashboard. Check logs."
            return (error_msg, "Error", [], [], [], error_msg, error_msg, error_msg, str(e))

    # Settings and other callbacks...
    pass
import pandas as pd # Add missing import for create_candles_table
