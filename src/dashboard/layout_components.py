from dash import dcc, html
import dash_bootstrap_components as dbc

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
                    html.Span("Leverage: ", className="text-muted"),
                    html.Span(id='header-leverage-display', children="10x", className="me-3"),
                    dcc.Dropdown(id='timeframe-selector',
                                 options=[{'label': tf, 'value': tf} for tf in ['1m', '5m', '15m', '1h', '4h', '1d']],
                                 value='1h', clearable=False, style={'width': '120px', 'color': 'black'}),
                    dbc.Button(html.I(className="fas fa-cog"), id="open-settings-button", color="secondary", className="ms-3"),
                    dbc.Button([html.I(className="fas fa-exclamation-triangle me-2"), "EMERGENCY"], id="emergency-kill-switch-button", color="danger", className="ms-3 fw-bold")
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
    return dcc.Tab(label="Multi-Timeframe Analysis", value="tab-multi-timeframe", children=[
        html.Div([
            dbc.Row([
                dbc.Col(html.H3("Multi-Timeframe Analysis"), width=6),
                dbc.Col(dcc.Dropdown(id="mtf-pair-selector", placeholder="Select Pair..."), width=6),
            ]),
            dbc.Card(dbc.CardBody(id='market-sentiment-card'), className="mb-4 mt-3"),
            html.Div(id='multi-timeframe-table', className="table-responsive"),
        ], className="p-3")
    ])

def create_trade_history_tab():
    return dcc.Tab(label="Trade History", value="tab-trade-history", children=[
        html.Div([
            html.H3("Completed Trades"),
            # Filters will be added here by callbacks
            html.Div(id='trade-history-table', className="table-responsive"),
        ], className="p-3")
    ])

def create_settings_offcanvas():
    # This is a simplified version of the settings panel from the user's code
    return dbc.Offcanvas(id="settings-offcanvas", title="Settings", is_open=False, placement="end", style={"width": "450px"}, children=[
        html.Div(id="settings-password-section", children=[
            html.H5("Enter Password"),
            dbc.Input(id="settings-password-input", type="password", placeholder="Enter password"),
            dbc.Button("Unlock", id="unlock-settings-button", color="primary", className="mt-2"),
        ]),
        html.Div(id="settings-content", style={"display": "none"}, children=[
            html.H5("General"),
            dcc.Checklist(id="auto-trading-toggle", options=[{'label': ' Automatic Trading', 'value': 'auto'}], value=['auto']),
            html.Hr(),
            html.H5("Strategies"),
            dcc.Checklist(id="strategy-checklist", options=[
                {'label': ' EMA CCI', 'value': 'main_strategy'},
                {'label': ' RSI CCI', 'value': 'rsi_cci_strategy'},
                {'label': ' TRF', 'value': 'trf_strategy'}
            ], value=['main_strategy']),
            html.Hr(),
            html.H5("Leverage"),
            dcc.Slider(id="leverage-slider", min=1, max=20, step=1, value=10),
            html.Hr(),
            dbc.Button("Apply Changes", id="apply-strategy-button", color="primary", className="w-100"),
            html.Div(id="settings-saved-message", className="text-success mt-2")
        ])
    ])

def create_kill_switch_modal():
    return dbc.Modal([
        dbc.ModalHeader(html.H4("EMERGENCY KILL SWITCH")),
        dbc.ModalBody(dbc.Alert("This will close all active positions immediately!", color="danger")),
        dbc.ModalFooter(dbc.Button("Close", id="kill-switch-close-button"))
    ], id="kill-switch-modal", is_open=False)

def get_full_layout():
    """Assembles the full dashboard layout."""
    return html.Div([
        dcc.Store(id='theme-store', data='dark'),
        dcc.Store(id='password-verified-store', data=False),
        dcc.Store(id='timeframe-store', data='1h'),
        dcc.Interval(id='refresh-interval', interval=15000, n_intervals=0),
        create_settings_offcanvas(),
        create_kill_switch_modal(),
        create_header(),
        dcc.Tabs(id="dashboard-tabs", value="tab-dashboard", className="custom-tabs", children=[
            create_dashboard_tab(),
            create_mtf_tab(),
            create_trade_history_tab(),
        ]),
    ])
