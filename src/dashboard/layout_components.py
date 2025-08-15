from dash import dcc, html
import dash_bootstrap_components as dbc

# Note: Some initial values are placeholders. They will be populated by callbacks.

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

def create_settings_offcanvas():
    return dbc.Offcanvas(id="settings-offcanvas", title="Settings", is_open=False, placement="end", children=[
        html.Div(id="settings-password-section", children=[
            html.H4("Enter Password"),
            dbc.Input(id="settings-password-input", type="password"),
            dbc.Button("Unlock", id="unlock-settings-button", color="primary"),
            html.Div(id="password-error-message", className="text-danger")
        ]),
        html.Div(id="settings-content", style={"display": "none"}, children=[
            html.H4("Trading Mode"),
            dcc.Checklist(id="auto-trading-toggle", options=[{'label': 'Automatic Trading', 'value': 'auto'}], value=['auto']),
            html.H4("Strategy Selection"),
            dcc.Checklist(id="strategy-checklist", options=[
                {'label': 'EMA CCI', 'value': 'main_strategy'},
                {'label': 'RSI CCI', 'value': 'rsi_cci_strategy'},
                {'label': 'TRF', 'value': 'trf_strategy'}
            ], value=['main_strategy']),
            html.H4("Leverage Settings"),
            dcc.Slider(id="leverage-slider", min=1, max=20, step=1, value=10),
            dbc.Button("Apply Changes", id="apply-strategy-button", color="primary", className="mt-3"),
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
            # Placeholders for other tabs
            dcc.Tab(label="Multi-Timeframe Analysis", value="tab-mtf"),
            dcc.Tab(label="Trade History", value="tab-history"),
        ]),
        # Hidden divs for triggering callbacks
        html.Div(id="_buy_trigger", style={"display": "none"}),
        html.Div(id="_sell_trigger", style={"display": "none"}),
        html.Div(id="_exit_trigger", style={"display": "none"}),
    ])
