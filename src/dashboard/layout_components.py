from dash import dcc, html
import dash_bootstrap_components as dbc

# This file contains functions that generate the layout components for the dashboard.

def create_header():
    # This function remains the same for now
    return html.Div(
        dbc.Row([
            dbc.Col(html.H1(id='header-title', children="SNIPER BOT V1"), width='auto'),
            dbc.Col(
                html.Div([
                    html.Span("Last Update: ", className="text-muted"),
                    html.Span(id='last-update-time', className="text-light me-3"),
                    html.Span("Status: ", className="text-muted"),
                    html.Span(id='status-indicator', className="px-2 rounded me-3"),
                    dcc.Dropdown(id='timeframe-selector',
                                 options=[{'label': tf, 'value': tf} for tf in ['1m', '5m', '15m', '1h', '4h', '1d']],
                                 value='1h', clearable=False, style={'width': '120px', 'color': 'black'}),
                    dbc.Button(html.I(className="fas fa-cog"), id="open-settings-button", color="secondary", className="ms-3"),
                ], className="d-flex align-items-center justify-content-end")
            )
        ], align="center", justify="between"),
        className="p-3 bg-dark text-white border-bottom"
    )

def create_settings_offcanvas():
    """Creates the full, detailed settings offcanvas."""
    return dbc.Offcanvas(id="settings-offcanvas", title="Settings", is_open=False, placement="end", style={"width": "450px"}, children=[
        html.Div(id="settings-password-section", children=[
            html.H5("Enter Password"),
            dbc.Input(id="settings-password-input", type="password", placeholder="Enter password"),
            dbc.Button("Unlock", id="unlock-settings-button", color="primary", className="mt-2"),
        ]),
        html.Div(id="settings-content", style={"display": "none"}, children=[
            dbc.Accordion([
                dbc.AccordionItem(title="General Settings", children=[
                    dcc.Checklist(id="auto-trading-toggle", options=[{'label': ' Automatic Trading', 'value': 'auto'}], value=['auto']),
                ]),
                dbc.AccordionItem(title="Strategy Selection", children=[
                    dcc.Checklist(id="strategy-checklist", options=[
                        {'label': ' EMA CCI', 'value': 'main_strategy'},
                        {'label': ' RSI CCI', 'value': 'rsi_cci_strategy'},
                        {'label': ' TRF', 'value': 'trf_strategy'}
                    ], value=['main_strategy']),
                ]),
                dbc.AccordionItem(title="Leverage & Risk", children=[
                    html.H6("Leverage"),
                    dcc.Slider(id="leverage-slider", min=1, max=20, step=1, value=10, marks={i: str(i) for i in range(1, 21, 2)}),
                    html.H6("TP/SL Override", className="mt-3"),
                    dcc.Checklist(id="tp-sl-override-toggle", options=[{'label': ' Enable TP/SL Override', 'value': True}]),
                    dcc.Input(id="override-take-profit", type="number", placeholder="Take Profit %", className="mt-2"),
                    dcc.Input(id="override-stop-loss", type="number", placeholder="Stop Loss %", className="mt-2"),
                ]),
                dbc.AccordionItem(title="Strategy Parameters", children=[
                    html.Div(id="strategy-parameters-display") # This will be populated by a callback
                ]),
            ], start_collapsed=True),
            dbc.Button("Apply Changes", id="apply-settings-button", color="primary", className="mt-4 w-100"),
            html.Div(id="settings-saved-message", className="text-success mt-2")
        ])
    ])

# Other layout functions remain the same...
def create_dashboard_tab():
    return dcc.Tab(label="Dashboard", value="tab-dashboard", children=[
        html.Div([
            dbc.Row([
                dbc.Col(dbc.Card([dbc.CardHeader("Bot Status"), dbc.CardBody(id='bot-status-card')]), width=4),
                dbc.Col(dbc.Card([dbc.CardHeader("Performance"), dbc.CardBody(id='performance-card')]), width=4),
                dbc.Col(dbc.Card([dbc.CardHeader("System Health"), dbc.CardBody(id='api-status-card')]), width=4),
            ]),
        ], className="p-3"),
        html.Div([html.H3("Technical Analysis"), html.Div(id='technicals-table')], className="p-3"),
        html.Div([html.H3("Active Positions"), html.Div(id='trades-table')], className="p-3"),
    ])

def get_full_layout():
    """Assembles the full dashboard layout."""
    return html.Div([
        dcc.Store(id='theme-store', data='dark'),
        dcc.Store(id='password-verified-store', data=False),
        dcc.Store(id='timeframe-store', data='1h'),
        dcc.Interval(id='refresh-interval', interval=15000, n_intervals=0),
        create_settings_offcanvas(),
        # create_kill_switch_modal(), # Add this back later
        create_header(),
        dcc.Tabs(id="dashboard-tabs", value="tab-dashboard", className="custom-tabs", children=[
            create_dashboard_tab(),
            # create_mtf_tab(),
            # create_trade_history_tab(),
        ]),
    ])
