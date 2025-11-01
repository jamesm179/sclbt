from dash import dcc, html
import dash_bootstrap_components as dbc
from src.config.config_manager import config_manager

def create_header():
    return html.Div(
        dbc.Row([
            dbc.Col(html.H1(id='header-title', children="SNIPER BOT V1"), width='auto'),
            dbc.Col(
                html.Div([
                    html.Span("Last Update: ", className="text-muted"),
                    html.Span(id='last-update-time', className="text-light me-3"),
                    html.Span("Status: ", className="text-muted"),
                    html.Span(id='status-indicator', className="px-2 rounded me-3"),
                    dcc.Dropdown(
                        id='timeframe-selector',
                        options=[
                            {'label': '1m', 'value': '1m'}, {'label': '5m', 'value': '5m'},
                            {'label': '15m', 'value': '15m'}, {'label': '1h', 'value': '1h'},
                            {'label': '4h', 'value': '4h'}, {'label': '1d', 'value': '1d'}
                        ],
                        value=config_manager.get('timeframe', '1h'),
                        clearable=False,
                        style={'width': '120px', 'color': 'black'}
                    ),
                    dbc.Button(html.I(className="fas fa-cog"), id="open-settings-button", color="secondary", className="ms-3"),
                ], className="d-flex align-items-center justify-content-end")
            )
        ], align="center", justify="between"),
        className="p-3 bg-dark text-white border-bottom"
    )

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
        html.Div([html.H3("Recent Market Data"), html.Div(id='candles-table')], className="p-3"),
        html.Div([html.H3("Event Log"), html.Pre(id='log-container', className="bg-secondary text-light p-3 rounded")], className="p-3"),
    ])

def create_mtf_tab():
    # ... (full implementation)
    return dcc.Tab(label="Multi-Timeframe Analysis", value="tab-multi-timeframe", children=[html.Div("MTF Content")])

def create_trade_history_tab():
    # ... (full implementation)
    return dcc.Tab(label="Trade History", value="tab-trade-history", children=[html.Div("History Content")])

def create_settings_offcanvas():
    return dbc.Offcanvas(id="settings-offcanvas", title="Settings", is_open=False, placement="end", style={"width": "450px"}, children=[
        html.Div(id="settings-content", children=[
            dbc.Accordion([
                dbc.AccordionItem(title="Theme & Colors", children=[
                    html.H6("Table Colors"),
                    html.Div([html.Label("Positive Color:"), dcc.Input(id="positive-color-input", type="color", value="#00FF00")]),
                    html.Div([html.Label("Negative Color:"), dcc.Input(id="negative-color-input", type="color", value="#FF0000")]),
                    html.Div([html.Label("Neutral Color:"), dcc.Input(id="neutral-color-input", type="color", value="#FFFFFF")]),
                ]),
                # ... other settings ...
            ], start_collapsed=True, always_open=True),
            dbc.Button("Apply Changes", id="apply-settings-button", color="primary", className="mt-4 w-100"),
        ])
    ])

def get_full_layout():
    return html.Div([
        dcc.Store(id='theme-store', data='dark'),
        dcc.Store(id='timeframe-store', data='1h'),
        dcc.Interval(id='refresh-interval', interval=15000),
        create_settings_offcanvas(),
        create_header(),
        dcc.Tabs(id="dashboard-tabs", value="tab-dashboard", children=[
            create_dashboard_tab(),
            create_mtf_tab(),
            create_trade_history_tab(),
        ]),
    ])
