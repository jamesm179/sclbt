import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from .layout_components import get_full_layout
from .callbacks import register_callbacks
from src.config.config_manager import config_manager

class DashboardApp:
    def __init__(self, trading_bot):
        self.bot = trading_bot
        theme = config_manager.get('theme', 'dark')
        theme_url = dbc.themes.DARKLY if theme == 'dark' else dbc.themes.LITERA

        # Add required external stylesheets for fonts and icons
        external_stylesheets = [
            theme_url,
            "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap",
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css"
        ]

        self.app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        self.app.title = "Sniper Bot V1 Dashboard"

        # Use the full layout from the layout_components module
        self.app.layout = get_full_layout()

        # Register all callbacks
        register_callbacks(self.app, self.bot)

    def run(self):
        self.app.run_server(debug=False, host='127.0.0.1', port=8050)
