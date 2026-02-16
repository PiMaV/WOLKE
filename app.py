import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import os
import socket
import logging
import io
import configparser

from data_loader import load_data
from layout import create_layout
from callbacks import register_numeric_callbacks, register_collapse_button_callbacks, register_categorical_callbacks, register_main_callbacks
from dash.exceptions import PreventUpdate
from flask_socketio import SocketIO
from flask import abort, send_file
from functions import harmonize_image, prdebug, prinfo, prerror, prwarn, generate_token, sort_categories
from dash import Dash
from state import state

# Initialize the Dash app (but don't run it yet)
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
socketio = SocketIO(server, async_mode="eventlet")

def load_config(config_file='config.ini'):
    """
    Loads configuration from the specified INI file.

    Args:
        config_file (str, optional): Path to the config file. Defaults to 'config.ini'.

    Returns:
        tuple: (root_dir, debug, port, plot_marginals)
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    
    # Extract settings with fallbacks to global defaults
    root_dir = config.get('settings', 'root_dir', fallback=state.ROOT_DIR)
    debug = config.getboolean('settings', 'debug', fallback=state.DEBUG)
    port = config.getint('settings', 'port', fallback=state.PORT)
    plot_marginals = config.get('settings', 'plot_marginals', fallback=state.PLOT_MARGINALS)
    
    return root_dir, debug, port, plot_marginals

def main():
    """Main entry point for the application."""
    # Load the configuration
    state.ROOT_DIR, state.DEBUG, state.PORT, state.PLOT_MARGINALS = load_config()

    # Set up logging
    if state.DEBUG:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Load data and initialize global variables
    all_categorical_options, all_numeric_options, DF = load_data(state.ROOT_DIR)
    state.DF = DF

    drop_list_num = []
    drop_list_cat = ['relative_filepath']

    # Remove dropped options from the 'all' lists
    all_categorical_options = [option for option in all_categorical_options if option['label'] not in drop_list_cat]
    all_numeric_options = [option for option in all_numeric_options if option['label'] not in drop_list_num]

    # Initialize 'selected' lists with the filtered 'all' lists
    state.selected_categorical_options = all_categorical_options.copy()
    state.selected_numeric_options = all_numeric_options.copy()

    # Generate token and full URL
    state.TOKEN = generate_token()
    FULL_URL = f"http://{socket.gethostbyname(socket.gethostname())}:{state.PORT}"
    
    prinfo(f"Token: {state.TOKEN}")
    prinfo(f"Full URL: {FULL_URL}")

    # Define the layout only after data is loaded
    app.layout = create_layout(state.DF, all_categorical_options, all_numeric_options, state.selected_categorical_options, state.selected_numeric_options, "v1.4", FULL_URL, state.TOKEN)

    register_categorical_callbacks(app, state.DF, all_categorical_options)
    register_numeric_callbacks(app, state.DF, all_numeric_options)
    register_collapse_button_callbacks(app)
    register_main_callbacks(app, state, socketio)
    
    app.secret_key = state.TOKEN

    # Run the Dash app
    prinfo(f"Running server on port {state.PORT} with DEBUG={state.DEBUG}...")
    socketio.run(server, host="0.0.0.0", debug=state.DEBUG, port=state.PORT)

@server.route('/<token>')
def get_selected_data(token):
    """
    Flask route to download selected data as a numpy array.

    Args:
        token (str): Security token to validate the request.

    Returns:
        Response: File download response or error.
    """
    prdebug(f"Selected rows: {state.selected_rows_global}")
    prinfo("Received request to get selected data.")

    if token == state.TOKEN:
        try:

            # Initialize an empty list to hold each selected numpy array
            selected_arrays = []

            for entry in state.selected_rows_global:
                relative_path = entry.get("relative_filepath")
                if not relative_path:
                    prwarn(f"No relative_filepath found in entry: {entry}")
                    continue  # Skip this entry if there's no file path
                
                safe_file_path = os.path.abspath(os.path.join(state.ROOT_DIR, relative_path))
                prdebug(f"Processing file: {safe_file_path}")

                if os.path.isfile(safe_file_path):
                    # Load the numpy array from the file
                    numpy_array = np.load(safe_file_path)
                    prdebug(f"Loaded numpy array shape: {numpy_array.shape}")
                    if state.HARMONIZE:
                        numpy_array = harmonize_image(numpy_array)
                        prdebug(f"Exposed Image harmonized")

                    # Add the processed array to the list
                    selected_arrays.append(numpy_array)
                else:
                    prwarn(f"File not found: {safe_file_path}")
                    return abort(404)  # File not found
            
            if not selected_arrays:
                prwarn("No files were found or processed.")
                return abort(404)  # No files were found or processed

            # Combine the selected arrays into a 3D array (stacking along a new axis)
            combined_array = np.stack(selected_arrays, axis=0)
            
            # Log the shape of the combined array
            prinfo(f"Combined array shape: {combined_array.shape}")

            # Save the combined array to a BytesIO stream
            output = io.BytesIO()
            np.save(output, combined_array)
            output.seek(0)  # Rewind the buffer to the beginning

            # Send the combined 3D array as a `.npy` file
            prinfo("Sending combined numpy array to client.")
            return send_file(output, mimetype='application/octet-stream', download_name='selected_data.npy')

        except Exception as e:
            prerror(f"Error: {str(e)}")
            return abort(400)  # Bad request
    prwarn("Invalid or missing token.")
    return abort(404)  # Not found or bad token


@socketio.on('connect')
def handle_connect():
    """Handles client connection."""
    prinfo('Client connected')
    socketio.emit('Connected successfully')
    prinfo('Connection response sent to client')

@socketio.on('disconnect')
def handle_disconnect():
    """Handles client disconnection."""
    prinfo('Client disconnected')

@socketio.on_error_default
def default_error_handler(e):
    """Handles socket errors."""
    prerror(f"An error occurred: {e}")

# Example for catching all incoming events
@socketio.on('*')
def catch_all(event, data):
    """Catches all socket events."""
    prinfo(f"Event received: {event} with data: {data}")

if __name__ == "__main__":
    main()
