"""
Create Dash app: config, state, data load, layout, callbacks, BLITZ endpoint.
"""
import logging
import os
import socket

import dash_bootstrap_components as dbc
from dash import Dash

from wolke.config import Config
from wolke.data.loader import DataLoader
from wolke.state import AppState
from wolke.utils import generate_token, prinfo
from wolke.web.blitz import BlitzHandler
from wolke.web.callbacks import register_callbacks
from wolke.web.layout import create_layout
from wolke.web.plotter import PlotGenerator

VERSION = "2.0.0"


def create_app(config_path: str | None = None) -> tuple[Dash, object, object, AppState, Config]:
    """
    Create and configure the Dash app, Flask server, SocketIO, AppState, and Config.
    Returns (app, server, socketio, state, config).
    """
    config = Config(config_path)
    logging.basicConfig(
        level=logging.DEBUG if config.debug else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    if not os.path.isfile(config.db_filename):
        raise FileNotFoundError(
            f"Database not found: {config.db_filename}\n"
            "Generate sample data from repo root: uv run python scripts/generate_sample_data.py"
        )
    prinfo(f"Using config: {config.config_path}")
    prinfo(f"Database: {config.db_filename}")
    loader = DataLoader(config.db_filename, config.table_name, config.image_base_dir)
    all_categorical, all_numeric, df = loader.load_data()
    prinfo(f"Loaded {len(df)} rows, {len(all_numeric)} numeric, {len(all_categorical)} categorical columns")

    plot_x = config.plot_x
    plot_y = config.plot_y
    plot_color = config.plot_color
    all_opts_labels = [o["label"] for o in all_numeric + all_categorical]
    if plot_x not in all_opts_labels:
        plot_x = all_numeric[0]["label"] if all_numeric else all_categorical[0]["label"]
    if plot_y not in all_opts_labels:
        plot_y = all_numeric[1]["label"] if len(all_numeric) > 1 else all_numeric[0]["label"] if all_numeric else all_categorical[0]["label"]
    if plot_color not in all_opts_labels:
        plot_color = all_numeric[0]["label"] if all_numeric else all_categorical[0]["label"]

    drop_path = [config.relative_filepath_column]
    all_categorical = [o for o in all_categorical if o["label"] not in drop_path]
    selected_categorical = all_categorical.copy()
    selected_numeric = all_numeric.copy()

    token = generate_token()
    try:
        host = socket.gethostbyname(socket.gethostname())
    except Exception:
        host = "127.0.0.1"
    full_url = f"http://{host}:{config.port}"
    prinfo(f"Token: {token}")
    prinfo(f"Full URL: {full_url}")

    state = AppState(
        df=df,
        image_base_dir=config.image_base_dir,
        relative_filepath_column=config.relative_filepath_column,
        token=token,
    )

    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    server = app.server
    socketio = __import__("flask_socketio").SocketIO(server, async_mode="eventlet")

    app.layout = create_layout(
        df,
        all_categorical,
        all_numeric,
        selected_categorical,
        selected_numeric,
        plot_x,
        plot_y,
        plot_color,
        VERSION,
        full_url,
        token,
    )
    app.secret_key = token

    plot_generator = PlotGenerator()
    register_callbacks(
        app,
        state,
        plot_generator,
        socketio,
        all_categorical,
        all_numeric,
        selected_categorical,
        selected_numeric,
    )

    BlitzHandler(server, socketio, state)
    prinfo(f"WOLKE initialized on port {config.port}, debug={config.debug}")

    return app, server, socketio, state, config
