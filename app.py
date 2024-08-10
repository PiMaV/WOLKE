import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import os
import random
import string
import socket
import logging
import io

from data_loader import load_data
from layout import create_layout
from callbacks import register_numeric_callbacks, register_collapse_button_callbacks, register_categorical_callbacks
from dash.exceptions import PreventUpdate
from flask_socketio import SocketIO
from flask import abort, request, send_from_directory, send_file
# from werkzeug.utils import safe_join
from functions import prinfo, harmonize_image
from dash import (
    Dash,
    dcc,
    Input,
    Output,
    no_update,
    State,
    callback_context,
    ALL,
)

# TODO:
# - Online Repository for the data
# - we need groupby per "imageset"
# - Numerics should be able to be deselected
# - x,y,z, in layout is hardcoded for multifil atm

# BUG:
# - Clicking on the histograms has a problem:   File "C:\INP\Projekte\Python\WOLKE\app.py", line 1050, in <listcomp>
    # point["customdata"][0] for point in selectedData["points"]

# IDEAS / INFO:
# - https://plotly.com/python/pca-visualization/  Suuuuuper interesting
# categories should be selectable beforehands (Maybe init file)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# GLOBALS !!!
PLOT_MARGINALS = 'violin'  # 'histogram' | 'violin'
DEBUG = True
PORT = 8050
VERSION = "v1.4"
ROOT_DIR = r"C:\Temp\Lukas_miniSub"
ROOT_DIR = r"C:\Temp\Lukas_50Subset_Full\subset"
SELECTED_ROWS = []


all_categorical_options, all_numeric_options, DF = load_data(ROOT_DIR)
drop_list_num = []
drop_list_cat = ['relative_filepath']
# Remove dropped options from the 'all' lists
all_categorical_options = [option for option in all_categorical_options if option['label'] not in drop_list_cat]
all_numeric_options = [option for option in all_numeric_options if option['label'] not in drop_list_num]
# Initialize 'selected' lists with the filtered 'all' lists
selected_categorical_options = all_categorical_options.copy()
selected_numeric_options = all_numeric_options.copy()

TOKEN = "".join(
    random.choices(string.ascii_letters + string.digits, k=8)
)
FULL_URL = f"http://{socket.gethostbyname(socket.gethostname())}:{PORT}"
prinfo(f"Token: {TOKEN}")
prinfo(f"Full URL: {FULL_URL}")


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  # CYBORG |PULSE | SLATE |BOOTSTRAP

# Initialize the Flask server
server = app.server
prinfo(f"Flask server initialized: {server}")

# Initialize SocketIO
socketio = SocketIO(server, async_mode="eventlet")
prinfo(f"SocketIO initialized with server: {server}")

# Optionally log the configuration details of SocketIO
prinfo(f"SocketIO async modes: {socketio.async_mode}")
prinfo(f"SocketIO message queue: {socketio.server.eio.ping_interval}, {socketio.server.eio.ping_timeout}")


app.layout = create_layout(DF, all_categorical_options, all_numeric_options, selected_categorical_options, selected_numeric_options, VERSION, FULL_URL, TOKEN)

register_categorical_callbacks(app, DF, all_categorical_options)
register_numeric_callbacks(app, DF, all_numeric_options)
register_collapse_button_callbacks(app)


def sort_categories(selected_column, df_filtered=None):
    if df_filtered is None:
        df_filtered = DF

    def convert_to_numeric(category_str):
        try:
            return float(category_str)  # Try converting to a number
        except ValueError:
            return category_str  # Treat as a non-numeric string

    logging.info(df_filtered.shape)
    all_categories = df_filtered[selected_column].unique()
    logging.info(f"Categories: {all_categories}")
    categories_as_numbers = [convert_to_numeric(cat) for cat in all_categories]
    # sort numerically if possible, otherwise alphabetically
    sorted_indices = np.argsort(categories_as_numbers)
    logging.info(f"Sorted Categories: {all_categories[sorted_indices]}")
    return all_categories[sorted_indices]


@app.callback(
    [
        Output("data-plot", "figure"),  # First output for the plot
        Output("info-table", "data"),  # Second output for the info box
    ],
    State("selected-cats-store", "data"),
    [
        Input("subset-range", "value"),
        Input("x-axis-dropdown", "value"),
        Input("y-axis-dropdown", "value"),
        Input("color-dropdown", "value"),
        Input({"type": "left-limit", "index": ALL}, "value"),
        Input({"type": "right-limit", "index": ALL}, "value"),
        Input({"type": "dynamic-dropdown", "index": ALL}, "value"),
        
    ]
)
def update_dataframe(
    selected_cat_options,
    subsample_ratio,
    x_column_name,
    y_column_name,
    cluster_column_name,
    all_left_limits,
    all_right_limits,
    *dropdown_values,
):
    # Input validation checks
    if not subsample_ratio:
        raise PreventUpdate
    if not x_column_name or not y_column_name:
        raise PreventUpdate
    if not all_left_limits or not all_right_limits:
        raise PreventUpdate
    if not dropdown_values or dropdown_values[0] is None:
        raise PreventUpdate
    

    df_filtered = DF.sample(frac=subsample_ratio, random_state=42)
    sub_shape = df_filtered.shape
    # df_filtered.rename(columns={"index": "original_index"}, inplace=True)
    logging.info(
        f"x: {x_column_name}, y: {y_column_name}, cluster_column: {cluster_column_name}"
    )
    logging.info(f"Dataframe size after subsampling: {df_filtered.shape}")
    logging.info(f"Selected Categorical Options: {selected_cat_options}")

    # Apply filters based on dropdown selections
    dropdown_values = dropdown_values[0]  # Unpack the list of lists
    for dropdown_value, option in zip(dropdown_values, selected_cat_options):
        column_name = option["value"]
        # logging.info(f"Column: {column_name}")
        logging.info(f"Dropdown Values {dropdown_value}")  # See the structure of dropdown_value
        if dropdown_value:  # Ensure the dropdown has selected values
            df_filtered = df_filtered[df_filtered[column_name].isin(dropdown_value)]
        else:
            raise PreventUpdate
    logging.info(f"Dataframe size after categorical filtering: {df_filtered.shape}")

    # Apply filters based on the left and right limits
    for index, option in enumerate(selected_numeric_options):
        column_name = option['value']
        if column_name in df_filtered.columns:
            left_limit = all_left_limits[index]
            right_limit = all_right_limits[index]
            if left_limit is not None and right_limit is not None:  # Check if limits are provided
                df_filtered = df_filtered[(df_filtered[column_name] >= left_limit) & (df_filtered[column_name] <= right_limit)]
                logging.info(f"Applied limits on {column_name}: Left {left_limit}, Right {right_limit}")
            else:
                logging.info(f"No limits applied to {column_name}")
    logging.info(f"Dataframe size after applying numeric limits: {df_filtered.shape}")

    if x_column_name in df_filtered.columns:
        if pd.api.types.is_numeric_dtype(DF[x_column_name]):
            logging.info("Numeric Handling")
            x_index = next((i for i, option in enumerate(selected_numeric_options) if option['label'] == x_column_name), None)
            logging.info(f"X-Index: {x_index}")
            logging.info(all_left_limits[x_index])
            logging.info(all_right_limits[x_index])

            df_filtered = df_filtered[
                (df_filtered[x_column_name] >= all_left_limits[x_index])
                & (df_filtered[x_column_name] <= all_right_limits[x_index])
            ]
            selected_categories = []
            logging.info(f"Dataframe size after X filtering: {df_filtered.shape}")
        else:  # Categorical Handling
            logging.info("Categorical Handling")
            selected_categories = sort_categories(x_column_name, df_filtered)
            # Search for the index of the first and last selected category in sorted_categories:
            # selected_categories = sorted_categories[x_range[0] : x_range[1] + 1]
            df_filtered = df_filtered[
                df_filtered[x_column_name].isin(selected_categories)
            ]

    if y_column_name in df_filtered.columns:
        if pd.api.types.is_numeric_dtype(DF[y_column_name]):
            logging.info("Numeric Handling")
            y_index = next((i for i, option in enumerate(selected_numeric_options) if option['label'] == y_column_name), None)
            logging.info(f"Y-Index: {y_index}")
            logging.info(all_left_limits[y_index])
            logging.info(all_right_limits[y_index])
            logging.info(f'Dataframe: {df_filtered.shape}')

            df_filtered = df_filtered[
                (df_filtered[y_column_name] >= all_left_limits[y_index])
                & (df_filtered[y_column_name] <= all_right_limits[y_index])
            ]
            selected_categories = []
            logging.info(f"Dataframe size after Y filtering: {df_filtered.shape}")
        else:  # Categorical Handling
            logging.info("Categorical Handling")
            selected_categories = sort_categories(y_column_name, df_filtered)
            # Search for the index of the first and last selected category in sorted_categories:
            # selected_categories = sorted_categories[y_range[0] : y_range[1] + 1]
            df_filtered = df_filtered[
                df_filtered[y_column_name].isin(selected_categories)
            ]

    logging.info(f"Dataframe size after X,Y filtering: {df_filtered.shape}")

    # logging.info(f"Selected Cluster Range: {cluster_range[0]}, {cluster_range[1]}")
    if cluster_column_name in df_filtered.columns:
        if pd.api.types.is_numeric_dtype(DF[cluster_column_name]):
            # if pd.api.types.is_numeric_dtype(df_filtered[cluster_column_name]):
            logging.info("Numeric Handling")
            cluster_index = next((i for i, option in enumerate(selected_numeric_options) if option['label'] == cluster_column_name), None)
            df_filtered = df_filtered[
                (df_filtered[cluster_column_name] >= all_left_limits[cluster_index])
                & (df_filtered[cluster_column_name] <= all_right_limits[cluster_index])
            ]
            selected_categories = []
        else:  # Categorical Handling
            logging.info("Categorical Handling")
            selected_categories = sort_categories(cluster_column_name, df_filtered)
            # Search for the index of the first and last selected category in sorted_categories:
            # selected_categories = sorted_categories[
                # cluster_range[0] : cluster_range[1] + 1
            # ]
            df_filtered = df_filtered[
                df_filtered[cluster_column_name].isin(selected_categories)
            ]

    logging.info(f"Dataframe size after Cluster filtering: {df_filtered.shape}")
    # logging.info(DF.info())
    # percent_filtered = (1 - df_filtered.shape[0] / sub_shape[0]) * 100
    # info_text = f"Org.: {DF.shape[0]}, Sub.: {sub_shape[0]}, Filtered: {df_filtered.shape[0]} | {percent_filtered:.2f}%"
    DF_shape = DF.shape[0]  # Total number of points in the original dataset
    sub_shape_value = sub_shape[
        0
    ]  # Assuming sub_shape is a tuple/list with the shape, take the first element
    filtered_shape = df_filtered.shape[0]  # Number of points after filtering

    # Calculate percentage based on the subsampled size
    percent_org = (
        DF_shape / sub_shape_value
    ) * 100  # This will give 200% if DF_shape is double sub_shape_value
    percent_filtered = (
        filtered_shape / sub_shape_value
    ) * 100  # Percentage of filtered data points relative to subsampled

    data_for_table = [
        {
            "Category": "Original",
            "Data Points": DF_shape,
            "Percent": f"{percent_org:.1f}%",
        },
        {"Category": "Subsampled", "Data Points": sub_shape_value, "Percent": "-"},
        {
            "Category": "Filtered",
            "Data Points": filtered_shape,
            "Percent": f"{percent_filtered:.1f}%",
        },
    ]
    # new_store_data = df_filtered.to_json(date_format="iso", orient="split")
    logging.info("Plotting...")
    fig = generate_plot(
        df_filtered,
        x_column_name,
        y_column_name,
        cluster_column_name,
        selected_categories,
    )

    return fig, data_for_table


def generate_plot(
    df_filtered, x_column_name, y_column_name, cluster_column_name, selected_categories
):
    # Print the dtype of the columns:
    logging.info(
        f"X: {df_filtered[x_column_name].dtype}, Y: {df_filtered[y_column_name].dtype}, Cluster: {df_filtered[cluster_column_name].dtype}, Selected Categories: {selected_categories}"
    )
    # min and max of peak_id
    # logging.info(
    #     f"Min / Max Peak ID: {df_filtered['peak_id'].min()}, {df_filtered['peak_id'].max()}"
    # )
    plot_type = "scatter"  # or "scatter_3d"

    if plot_type == "scatter":
        fig = px.scatter(
            df_filtered,
            x=x_column_name,
            y=y_column_name,
            color=cluster_column_name,
            category_orders={cluster_column_name: selected_categories},
            custom_data=["id"],
            marginal_x=PLOT_MARGINALS,
            marginal_y=PLOT_MARGINALS,
            
        )
        # fig.data[1].nbinsx =512 #TODO: This must be dynamic
        # fig.data[1].nbinsy =512 #TODO: This must be dynamic
        fig.update_layout(
            hovermode="closest",
            height=800,
            clickmode="event+select",                
            # scattermode="group",
            # scattergap=0.75
        )

    return fig

# DATA TABLE Callback
@app.callback(
    [
        Output("data-table", "data"),  # Update the data of the DataTable
        Output("image-selection", "data"),  # Now updating the dcc.Store
    ],
    [
        Input("data-plot", "selectedData"),  # Listen for box or lasso selections on the scatter plot
        Input("data-plot", "clickData"),  # Listen for single point clicks on the scatter plot
        Input("data-table", "active_cell"),  # Listen for cell activations in the DataTable
    ],
    [State("data-table", "data")],  # Current data of the DataTable
)
def display_selected_data_and_image(selectedData, clickData, active_cell, rows_data):
    global selected_rows_global
    ctx = callback_context

    if not ctx.triggered:
        return no_update, {}

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    store_out = {}

    logging.info(f"callback_context: {callback_context}")
    logging.info(f"Triggered ID: {triggered_id}")
    logging.info(f"Selected Data: {selectedData}")
    logging.info(f"Click Data: {clickData}")
    logging.info(f"Active Cell: {active_cell}")

    if triggered_id == "data-plot" and selectedData:
        # Extract the IDs from the selected points
        original_indices = [
            point["customdata"][0] for point in selectedData["points"]
        ]
        
        # Filter the DataFrame based on these IDs
        selected_rows = DF.loc[DF["id"].isin(original_indices)]
        
        if not selected_rows.empty:
            store_out = selected_rows.iloc[0][
                ["relative_filepath"]
            ].to_dict()
            
            table_data = selected_rows.to_dict("records")
            
            # Update the global variable with the selected rows
            selected_rows_global = table_data
            
            return table_data, store_out

    elif triggered_id == "data-table" and active_cell and rows_data:
        row = rows_data[active_cell["row"]]
        store_out = {
            "relative_filepath": row["relative_filepath"],
        }
        return no_update, store_out

    # If no relevant interaction, return no updates
    return no_update, {}

# IMAGE DISPLAY
@app.callback(
    Output(
        "numpy-container", "children"
    ),  # Update the container with the numpy content
    Input("image-selection", "data"),  # When the store is updated
)
def display_numpy_image(data_store_content):
    # Check if data_store_content is not empty and contains required keys
    logging.info(f"Data Store Content: {data_store_content}")
    if data_store_content and all(
        k in data_store_content
        for k in ["relative_filepath"]
    ):
        relative_filepath = data_store_content["relative_filepath"]
        # image_number = 0
        # image_number = data_store_content["image_number"]
        # position = data_store_content["position"]

        # Construct the full path to the numpy file
        full_file_path = os.path.join(ROOT_DIR, relative_filepath)
        socketio.emit("send_file_message",{"file_name":relative_filepath})
        logging.info(f"Full File Path: {full_file_path}")

        # Load the numpy file
        numpy_array = np.load(full_file_path)
        logging.info(f"Loaded Numpy Array: {numpy_array.shape}")

        # Assuming the numpy array can be indexed directly with image_number
        # Adjust as necessary if your data structure is different
        image_to_display = numpy_array
        
        image_to_display = harmonize_image(image_to_display)

        # Use Plotly to create a figure from the numpy array
        fig = px.imshow(image_to_display)
        # Plot the position as a vertical line
        # fig.add_vline(x=position, line_dash="dash", line_color="red")

        fig.update_layout(
            # width=1024,  # Set the figure width to a constant value
            autosize=True,  # Enable autosize to make the figure responsive
            # height=auto,  # Let Plotly adjust the height automatically based on the aspect ratio of the image
            margin=dict(l=20, r=20, t=20, b=20),  # Optional: adjust margins as needed
        )

        # Return the figure to be displayed in the container
        return dcc.Graph(figure=fig)

    # If no data is selected or store content is not in the expected format
    return "No image selected or file path unavailable."


@server.route('/<token>')
def get_selected_data(token):
    global selected_rows_global
    prinfo(f"Selected rows: {selected_rows_global}")
    prinfo("Received request to get selected data.")

    if token == TOKEN:
        try:
            prinfo(f"Selected rows: {selected_rows_global}")

            # Initialize an empty list to hold each selected numpy array
            selected_arrays = []

            for entry in selected_rows_global:
                relative_path = entry.get("relative_filepath")
                if not relative_path:
                    prinfo(f"No relative_filepath found in entry: {entry}")
                    continue  # Skip this entry if there's no file path
                
                safe_file_path = os.path.abspath(os.path.join(ROOT_DIR, relative_path))
                prinfo(f"Processing file: {safe_file_path}")

                if os.path.isfile(safe_file_path):
                    # Load the numpy array from the file
                    numpy_array = np.load(safe_file_path)
                    prinfo(f"Loaded numpy array shape: {numpy_array.shape}")

                    # Optional: Process the array (e.g., harmonize the image)
                    numpy_array = harmonize_image(numpy_array)
                    prinfo(f"Processed numpy array shape: {numpy_array.shape}")

                    # Add the processed array to the list
                    selected_arrays.append(numpy_array)
                else:
                    prinfo(f"File not found: {safe_file_path}")
                    return abort(404)  # File not found
            
            if not selected_arrays:
                prinfo("No files were found or processed.")
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
            prinfo(f"Error: {str(e)}")
            return abort(400)  # Bad request
    prinfo("Invalid or missing token.")
    return abort(404)  # Not found or bad token


@socketio.on('connect')
def handle_connect():
    prinfo('Client connected')
    socketio.emit('Connected successfully')
    prinfo('Connection response sent to client')

@socketio.on('disconnect')
def handle_disconnect():
    prinfo('Client disconnected')

@socketio.on_error_default
def default_error_handler(e):
    prinfo(f"An error occurred: {e}")

# Example for catching all incoming events
@socketio.on('*')
def catch_all(event, data):
    prinfo(f"Event received: {event} with data: {data}")


# DOWNLOAD BUTTON
@app.callback(
    Output("download-dataset", "data"),
    Input("btn_image", "n_clicks"),
    State("image-selection", "data"),  # Access the store as a state
    prevent_initial_call=True,
)
def func(n_clicks, data_store_content):
    if data_store_content and "relative_filepath" in data_store_content:
        relative_filepath = data_store_content["relative_filepath"]
        # Assuming FOLDER_PATH is defined globally or within this function's scope
        full_file_path = os.path.join(ROOT_DIR, relative_filepath)

        # Use dcc.send_file to initiate downloading the file at the specified path
        return dcc.send_file(full_file_path)
    else:
        # Handle the case where the data store is empty or does not contain the expected keys
        # You might want to return an error message or a specific behavior
        return None


if __name__ == "__main__":
    
    prinfo(f"Running server on port {PORT} with DEBUG={DEBUG}...")
    socketio.run(server, host="0.0.0.0", debug=DEBUG, port=PORT) 
    # app.run_server(debug=DEBUG)
    #app.run_server(debug=DEBUG, host="0.0.0.0", port=PORT)
