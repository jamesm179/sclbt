from dash import dcc, html
import dash_bootstrap_components as dbc

# This file contains functions that generate the layout components for the dashboard.

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
    # ... (code for settings offcanvas)
    return dbc.Offcanvas(id="settings-offcanvas", title="Settings", is_open=False)

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
            dbc.Row([
                dbc.Col(dcc.Dropdown(id='trade-history-pair-filter', placeholder="Filter by Pair..."), width=3),
                dbc.Col(dcc.Dropdown(id='trade-history-strategy-filter', placeholder="Filter by Strategy..."), width=3),
            ], className="mb-3"),
            html.Div(id='trade-history-table', className="table-responsive"),
        ], className="p-3")
    ])

def get_full_layout():
    """Assembles the full dashboard layout."""
    return html.Div([
        dcc.Store(id='theme-store', data='dark'),
        dcc.Store(id='password-verified-store', data=False),
        dcc.Store(id='timeframe-store', data='1h'),
        dcc.Interval(id='refresh-interval', interval=15000, n_intervals=0),
        create_settings_offcanvas(),
        create_header(),
        dcc.Tabs(id="dashboard-tabs", value="tab-dashboard", className="custom-tabs", children=[
            create_dashboard_tab(),
            create_mtf_tab(),
            create_trade_history_tab(),
        ]),
    ])
