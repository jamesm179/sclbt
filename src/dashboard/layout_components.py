from dash import dcc, html
import dash_bootstrap_components as dbc

# Note: The initial values for components like Dropdowns will be populated by callbacks.
# We define the structure here.

def create_header():
    return html.Div([
        html.Div([
            html.H1(id='header-title', children="SNIPER BOT V1"),
            html.Div([
                html.Span("Last Update: ", className="text-muted"),
                html.Span(id='last-update-time', className="text-light"),
                html.Span(" | Status: ", className="text-muted"),
                html.Span(id='status-indicator', className="px-2 rounded"),
                html.Span(" | Leverage: ", className="text-muted"),
                html.Span(id='header-leverage-display', children="10x"),
                dbc.Button(html.I(className="fas fa-cog"), id="open-settings-button", color="secondary", className="ms-3"),
                dbc.Button([html.I(className="fas fa-exclamation-triangle me-2"), "EMERGENCY EXIT"], id="emergency-kill-switch-button", color="danger", className="ms-3 fw-bold")
            ], className="d-flex align-items-center")
        ], className="d-flex align-items-center justify-content-between")
    ], className="p-3 bg-dark text-white border-bottom")

def create_dashboard_tab():
    return dcc.Tab(label="Dashboard", value="tab-dashboard", className="custom-tab", selected_className="custom-tab--selected", children=[
        html.Div([
            html.H3("Market Overview"),
            dbc.Row([
                dbc.Col(dbc.Card([dbc.CardHeader("Bot Status"), dbc.CardBody(id='bot-status-card')]), width=4),
                dbc.Col(dbc.Card([dbc.CardHeader("Performance"), dbc.CardBody(id='performance-card')]), width=4),
                dbc.Col(dbc.Card([dbc.CardHeader("API Status"), dbc.CardBody(id='api-status-card')]), width=4),
            ]),
        ], className="p-3"),
        html.Div([html.H3("Technical Indicators"), html.Div(id='technicals-table')], className="p-3"),
        html.Div([html.H3("Active Positions"), html.Div(id='trades-table')], className="p-3"),
        html.Div([html.H3("Recent Candles"), html.Div(id='candles-table')], className="p-3"),
        html.Div([html.H3("Log Messages"), html.Pre(id='log-container', className="bg-dark text-light p-3 rounded")], className="p-3"),
    ])

def create_mtf_tab():
    return dcc.Tab(label="Multi-Timeframe Analysis", value="tab-multi-timeframe", className="custom-tab", selected_className="custom-tab--selected", children=[
        html.Div([
            dbc.Row([
                dbc.Col(html.H3("Multi-Timeframe Technical Analysis"), width=6),
                dbc.Col(dcc.Dropdown(id="mtf-pair-selector", placeholder="Select a trading pair..."), width=6),
            ]),
            dbc.Card(dbc.CardBody(id='market-sentiment-card'), className="mb-4"),
            html.Div(id='multi-timeframe-table', className="table-responsive"),
        ], className="p-3")
    ])

def create_trade_history_tab():
    return dcc.Tab(label="Trade History", value="tab-trade-history", className="custom-tab", selected_className="custom-tab--selected", children=[
        html.Div([
            html.H3("Trade History"),
            # Add filters for history table here
            html.Div(id='trade-history-table', className="table-responsive"),
        ], className="p-3")
    ])

def create_settings_offcanvas():
    return dbc.Offcanvas(id="settings-offcanvas", title="Settings", is_open=False, placement="end", style={"width": "400px"}, children=[
        html.Div(id="settings-password-section", children=[
            html.H4("Enter Password"),
            dbc.Input(id="settings-password-input", type="password", placeholder="Enter password"),
            dbc.Button("Unlock", id="unlock-settings-button", color="primary", className="mt-2"),
            html.Div(id="password-error-message", className="text-danger mt-2")
        ]),
        html.Div(id="settings-content", style={"display": "none"}, children=[
            # General Settings
            html.H4("General Settings", className="mt-3"),
            dcc.Checklist(id="auto-trading-toggle", options=[{'label': ' Automatic Trading', 'value': 'auto'}], value=['auto']),
            dcc.Checklist(id="auto-browser-toggle", options=[{'label': ' Auto-open Browser on Startup', 'value': 'auto'}], value=['auto']),

            # Theme & Timeframe
            html.H4("Display", className="mt-3"),
            dcc.Dropdown(id="theme-selector-header", options=[{'label': 'Dark', 'value': 'dark'}, {'label': 'Light', 'value': 'light'}], value='dark'),
            dcc.Dropdown(id="timeframe-selector", options=[{'label': '1h', 'value': '1h'}, {'label': '4h', 'value': '4h'}], value='1h'),

            # Strategy Selection
            html.H4("Strategy Selection", className="mt-3"),
            dcc.Checklist(id="strategy-checklist", options=[
                {'label': ' EMA CCI Strategy', 'value': 'main_strategy'},
                {'label': ' RSI CCI Strategy', 'value': 'rsi_cci_strategy'},
                {'label': ' TRF Strategy', 'value': 'trf_strategy'}
            ], value=['main_strategy']),

            # Leverage Settings
            html.H4("Leverage", className="mt-3"),
            dcc.Slider(id="leverage-slider", min=1, max=20, step=1, value=10, marks={i: str(i) for i in range(1, 21, 2)}),

            # TP/SL Override
            html.H4("TP/SL Override", className="mt-3"),
            dcc.Checklist(id="tp-sl-override-toggle", options=[{'label': ' Enable TP/SL Override', 'value': True}]),
            dcc.Input(id="override-take-profit", type="number", placeholder="Take Profit %"),
            dcc.Input(id="override-stop-loss", type="number", placeholder="Stop Loss %"),

            # Trailing Stop Loss
            html.H4("Dynamic Trailing Stop-Loss", className="mt-3"),
            dcc.Checklist(id="trailing-stop-toggle", options=[{'label': ' Enable Trailing Stop', 'value': True}]),

            # Manual Trading Pairs
            html.H4("Manual Trading Pairs", className="mt-3"),
            dbc.Input(id="new-pair-input", placeholder="e.g., GALA/USDT"),
            dbc.Button("Add Pair", id="add-pair-button", color="success"),
            html.Div(id="manual-pairs-display"),

            # Apply Button
            dbc.Button("Apply Changes", id="apply-strategy-button", color="primary", className="mt-4 w-100"),
            html.Div(id="settings-saved-message", className="text-success mt-2")
        ])
    ])

def create_kill_switch_modal():
    return dbc.Modal([
        dbc.ModalHeader(html.H4("EMERGENCY KILL SWITCH", className="text-danger")),
        dbc.ModalBody([
            dbc.Alert("This will IMMEDIATELY close ALL active positions!", color="danger"),
            dbc.Input(id="kill-switch-password-input", type="password", placeholder="Enter settings password"),
            html.Div(id="kill-switch-password-error", className="text-danger")
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="kill-switch-cancel-button", color="secondary"),
            dbc.Button("EXECUTE", id="kill-switch-execute-button", color="danger"),
        ])
    ], id="kill-switch-modal", is_open=False)

def get_full_layout():
    return html.Div([
        dcc.Store(id='theme-store', data='dark'),
        dcc.Store(id='password-verified-store', data=False),
        dcc.Store(id='timeframe-store', data='1h'),
        dcc.Store(id='active-strategies-store', data=['main_strategy']),
        dcc.Interval(id='refresh-interval', interval=15000, n_intervals=0),

        create_settings_offcanvas(),
        create_kill_switch_modal(),
        create_header(),
        dcc.Tabs(id="dashboard-tabs", value="tab-dashboard", className="custom-tabs", children=[
            create_dashboard_tab(),
            create_mtf_tab(),
            create_trade_history_tab(),
        ]),

        # Hidden divs for triggering callbacks without a direct user interaction
        html.Div(id="_buy_trigger", style={"display": "none"}),
        html.Div(id="_sell_trigger", style={"display": "none"}),
        html.Div(id="_exit_trigger", style={"display": "none"}),
    ])
