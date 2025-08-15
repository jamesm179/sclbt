from dash import dcc, html
import dash_bootstrap_components as dbc

# This file contains functions that generate the layout components for the dashboard.
# This modular approach keeps the main app file cleaner.

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
                dcc.Dropdown(id='timeframe-selector',
                             options=[{'label': '1h', 'value': '1h'}, {'label': '4h', 'value': '4h'}, {'label': '1d', 'value': '1d'}],
                             value='1h', clearable=False, style={'width': '140px', 'color': 'black'}),
                dbc.Button(html.I(className="fas fa-cog"), id="open-settings-button", color="secondary", className="ms-3"),
                dbc.Button([html.I(className="fas fa-exclamation-triangle me-2"), "EMERGENCY"], id="emergency-kill-switch-button", color="danger", className="ms-3 fw-bold")
            ], className="d-flex align-items-center")
        ], className="d-flex align-items-center justify-content-between")
    ], className="p-3 bg-dark text-white border-bottom")

def create_dashboard_tab():
    return dcc.Tab(label="Dashboard", value="tab-dashboard", children=[
        html.Div([
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
    return dbc.Offcanvas(id="settings-offcanvas", title="Settings", is_open=False, placement="end", style={"width": "400px"}, children=[
        html.Div(id="settings-password-section", children=[
            html.H4("Enter Password"),
            dbc.Input(id="settings-password-input", type="password", placeholder="Enter password"),
            dbc.Button("Unlock", id="unlock-settings-button", color="primary", className="mt-2"),
            html.Div(id="password-error-message", className="text-danger mt-2")
        ]),
        html.Div(id="settings-content", style={"display": "none"}, children=[
            # Full settings content will be added here
            html.P("Settings controls will be populated here.")
        ])
    ])

def create_kill_switch_modal():
    return dbc.Modal([
        dbc.ModalHeader(html.H4("EMERGENCY KILL SWITCH")),
        dbc.ModalBody(dbc.Alert("This will IMMEDIATELY close ALL active positions!", color="danger")),
        dbc.ModalFooter(dbc.Button("Close", id="kill-switch-close-button", className="ms-auto", n_clicks=0))
    ], id="kill-switch-modal", is_open=False)

def get_full_layout():
    """Assembles and returns the full layout of the dashboard."""
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
            # Other tabs will be added here
        ]),
    ])
