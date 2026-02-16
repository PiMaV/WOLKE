import logging
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import Dash, Input, Output, MATCH, State, callback_context, dcc, no_update, ALL
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
import os
import plotly.express as px
from functions import create_histogram_figure, prinfo, prdebug, prerror, prwarn, harmonize_image, sort_categories, generate_plot

def register_numeric_callbacks(app: Dash, DF: pd.DataFrame, all_numeric_options: list):
    """
    Registers callbacks for numeric range selection using histograms.

    Args:
        app (Dash): The Dash application instance.
        DF (pd.DataFrame): The main dataframe.
        all_numeric_options (list): List of numeric column options.
    """
    @app.callback(
        Output({"type": "histogram-graph", "index": MATCH}, "figure"),
        [
            Input({"type": "left-limit", "index": MATCH}, "value"),
            Input({"type": "right-limit", "index": MATCH}, "value"),
            Input("selected-nums-store", "data"),
        ],
        State({"type": "histogram-graph", "index": MATCH}, "id"),
    )
    def update_graph(left_limit, right_limit, selected_nums, id):
        """Updates the histogram graph based on limits and selection."""
        selected_options = [
            option
            for option in all_numeric_options
            if option["label"]
            in [cat["label"] for cat in selected_nums]  # Extract labels
        ]
        index = id["index"]
        column_name = selected_options[index]["label"]
        fig = create_histogram_figure(DF, column_name)
        fig.update_layout(
            xaxis_range=[left_limit, right_limit],
        )
        return fig

    @app.callback(
        [
            Output({"type": "left-limit", "index": MATCH}, "value"),
            Output({"type": "right-limit", "index": MATCH}, "value"),
        ],
        [
            Input({"type": "histogram-graph", "index": MATCH}, "relayoutData"),
            Input("reset-button-nums", "n_clicks")
        ],
        [
            State({"type": "left-limit", "index": MATCH}, "value"),
            State({"type": "right-limit", "index": MATCH}, "value"),
            State({"type": "histogram-graph", "index": MATCH}, "id"),
            State("selected-nums-store", "data"),
        ],
    )
    def update_limits(
        relayoutData, n_clicks, left_limit_state, right_limit_state, id, selected_nums
    ):
        """Updates the numeric limits based on histogram interaction or reset."""
        ctx = callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if triggered_id == "reset-button-nums":
            selected_options = [
                option
                for option in all_numeric_options
                if option["label"]
                in [cat["label"] for cat in selected_nums]
            ]
            index = id["index"]
            column_name = selected_options[index]["value"]
            return DF[column_name].min(), DF[column_name].max()

        if relayoutData and (
            "autosize" in relayoutData
            or (
                "xaxis.range[0]" not in relayoutData
                and "xaxis.range[1]" not in relayoutData
            )
        ):
            selected_options = [
                option
                for option in all_numeric_options
                if option["label"]
                in [cat["label"] for cat in selected_nums]
            ]
            index = id["index"]
            column_name = selected_options[index]["value"]
            return DF[column_name].min(), DF[column_name].max()

        elif (
            relayoutData
            and "xaxis.range[0]" in relayoutData
            and "xaxis.range[1]" in relayoutData
        ):
            return float(relayoutData["xaxis.range[0]"]), float(relayoutData["xaxis.range[1]"])
            
        return left_limit_state, right_limit_state


def register_collapse_button_callbacks(app: Dash):
    """
    Registers callbacks for collapsing/expanding layout sections.

    Args:
        app (Dash): The Dash application instance.
    """
    @app.callback(
        Output("collapse-feature-graphs", "is_open"),
        [Input("collapse-button-graphs", "n_clicks")],
        [State("collapse-feature-graphs", "is_open")],
    )
    def toggle_collapse_graphs(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse-feature-subset", "is_open"),
        [Input("collapse-button-subset", "n_clicks")],
        [State("collapse-feature-subset", "is_open")],
    )
    def toggle_collapse_subset(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse-feature-categories", "is_open"),
        [Input("collapse-button-categories", "n_clicks")],
        [State("collapse-feature-categories", "is_open")],
    )
    def toggle_collapse_categories(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse-axis-dropdowns", "is_open"),
        [Input("collapse-button-axis-dropdowns", "n_clicks")],
        [State("collapse-axis-dropdowns", "is_open")],
    )
    def toggle_collapse_axis(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse-feature-histograms", "is_open"),
        [Input("collapse-button-histograms", "n_clicks")],
        [State("collapse-feature-histograms", "is_open")],
    )
    def toggle_collapse_histograms(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open


def register_categorical_callbacks(app: Dash, DF: pd.DataFrame, all_categorical_options: list):
    """
    Registers callbacks for categorical selection and dynamic dropdowns.

    Args:
        app (Dash): The Dash application instance.
        DF (pd.DataFrame): The main dataframe.
        all_categorical_options (list): List of categorical column options.
    """
    logging.info("CAT: Registering categorical callbacks...")
    
    @app.callback(
        Output("cat-dropdown-container", "children"),
        Input("selected-cats-store", "data"),
    )
    def generate_dynamic_dropdowns(selected_cats):
        """Generates dynamic dropdowns based on selected categories."""
        selected_options = [
            option
            for option in all_categorical_options
            if option["label"]
            in [cat["label"] for cat in selected_cats]
        ]
        dropdowns = []
        for option in selected_options:
            dropdown = dbc.Row(
                [
                    dbc.Col(
                        dmc.Select(
                            id={"type": "dynamic-row", "index": option["value"]},
                            data=[option["label"]],
                            value=option["label"],
                            clearable=True,
                        ),
                        width=2,
                    ),
                    dbc.Col(
                        dmc.MultiSelect(
                            id={"type": "dynamic-dropdown", "index": option["value"]},
                            data=[
                                {"label": cat, "value": cat}
                                for cat in DF[option["value"]].unique()
                            ],
                            value=DF[option["value"]].unique().tolist(),
                            clearable=True,
                            searchable=True,
                        ),
                        width=10,
                    ),
                ],
                className="mb-3",
            )
            dropdowns.append(dropdown)
        return dropdowns

    @app.callback(
        Output({'type': 'dynamic-dropdown', 'index': ALL}, 'value'),
        [Input("reset-button", "n_clicks")],
        State("selected-cats-store", "data"),
        prevent_initial_call=True
    )
    def reset_dropdowns(n_clicks, selected_cat_options):
        """Resets all categorical dropdowns to their full range."""
        if n_clicks is None:
            raise PreventUpdate

        logging.info(f"CAT: Resetting categories...")
        reset_values = []
        for option in selected_cat_options:
            reset_value = DF[option["value"]].unique().tolist()
            reset_values.append(reset_value)
        
        logging.info(f"Reset values: {reset_values}")
        return reset_values

    @app.callback(
        Output("cat-available-container", "data"),
        Output("cat-available-container", "value"),
        Output("selected-cats-store", "data"),
        Output("x-axis-dropdown", "options"),
        Output("y-axis-dropdown", "options"),
        Output("color-dropdown", "options"),
        Input({"type": "dynamic-row", "index": ALL}, "value"),
        Input("cat-available-container", "value"),
        State("selected-cats-store", "data"),
        State("selected-nums-store", "data"),
    )
    def update_available_categories(dynamic_row, available_values, stored_data, selected_numeric):
        """Updates available categories for selection and moves them between containers."""
        logging.info("CAT: Update available categories callback triggered...")
        if not stored_data:
            stored_data = []

        if dynamic_row:  
            changed_index = [i for i, item in enumerate(dynamic_row) if not item]

            for index in sorted(changed_index, reverse=True):
                label_to_move = stored_data[index]["label"] 
                del stored_data[index]
                available_values.append(label_to_move) 

            available_values.sort()

        available_options = [
            option
            for option in all_categorical_options
            if option["label"] in available_values
        ]
        updated_store = [
            option
            for option in all_categorical_options
            if option["label"] not in available_values
        ]

        available_axis_options = updated_store + selected_numeric

        return available_options, available_values, updated_store, available_axis_options, available_axis_options, available_axis_options

def register_plot_callbacks(app: Dash, state):
    """
    Registers callbacks for the main scatter plot and data table.

    Args:
        app (Dash): The Dash application instance.
        state (AppState): The shared application state.
    """
    @app.callback(
        [
            Output("data-plot", "figure"),
            Output("info-table", "data"),
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
        """Filters the dataframe based on all inputs and updates the scatter plot."""
        DF = state.DF
        selected_numeric_options = state.selected_numeric_options
        PLOT_MARGINALS = state.PLOT_MARGINALS

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

        # Apply filters based on dropdown selections
        dropdown_values = dropdown_values[0]
        for dropdown_value, option in zip(dropdown_values, selected_cat_options):
            column_name = option["value"]
            if dropdown_value:
                df_filtered = df_filtered[df_filtered[column_name].isin(dropdown_value)]
            else:
                raise PreventUpdate

        # Apply filters based on numeric limits
        for index, option in enumerate(selected_numeric_options):
            column_name = option['value']
            if column_name in df_filtered.columns:
                left_limit = all_left_limits[index]
                right_limit = all_right_limits[index]
                if left_limit is not None and right_limit is not None:
                    df_filtered = df_filtered[(df_filtered[column_name] >= left_limit) & (df_filtered[column_name] <= right_limit)]

        # Filter X axis
        if x_column_name in df_filtered.columns:
            if pd.api.types.is_numeric_dtype(DF[x_column_name]):
                x_index = next((i for i, option in enumerate(selected_numeric_options) if option['label'] == x_column_name), None)
                df_filtered = df_filtered[
                    (df_filtered[x_column_name] >= all_left_limits[x_index])
                    & (df_filtered[x_column_name] <= all_right_limits[x_index])
                ]
                selected_categories = []
            else:
                selected_categories = sort_categories(DF, x_column_name, df_filtered)
                df_filtered = df_filtered[
                    df_filtered[x_column_name].isin(selected_categories)
                ]

        # Filter Y axis
        if y_column_name in df_filtered.columns:
            if pd.api.types.is_numeric_dtype(DF[y_column_name]):
                y_index = next((i for i, option in enumerate(selected_numeric_options) if option['label'] == y_column_name), None)
                df_filtered = df_filtered[
                    (df_filtered[y_column_name] >= all_left_limits[y_index])
                    & (df_filtered[y_column_name] <= all_right_limits[y_index])
                ]
                selected_categories = []
            else:
                selected_categories = sort_categories(DF, y_column_name, df_filtered)
                df_filtered = df_filtered[
                    df_filtered[y_column_name].isin(selected_categories)
                ]

        # Filter Color/Cluster
        if cluster_column_name in df_filtered.columns:
            if pd.api.types.is_numeric_dtype(DF[cluster_column_name]):
                cluster_index = next((i for i, option in enumerate(selected_numeric_options) if option['label'] == cluster_column_name), None)
                df_filtered = df_filtered[
                    (df_filtered[cluster_column_name] >= all_left_limits[cluster_index])
                    & (df_filtered[cluster_column_name] <= all_right_limits[cluster_index])
                ]
                selected_categories = []
            else:
                selected_categories = sort_categories(DF, cluster_column_name, df_filtered)
                df_filtered = df_filtered[
                    df_filtered[cluster_column_name].isin(selected_categories)
                ]

        DF_shape = DF.shape[0]
        sub_shape_value = sub_shape[0]
        filtered_shape = df_filtered.shape[0]

        percent_org = (DF_shape / sub_shape_value) * 100
        percent_filtered = (filtered_shape / sub_shape_value) * 100

        data_for_table = [
            {"Category": "Original", "Data Points": DF_shape, "Percent": f"{percent_org:.1f}%"},
            {"Category": "Subsampled", "Data Points": sub_shape_value, "Percent": "-"},
            {"Category": "Filtered", "Data Points": filtered_shape, "Percent": f"{percent_filtered:.1f}%"},
        ]

        fig = generate_plot(
            df_filtered,
            x_column_name,
            y_column_name,
            cluster_column_name,
            selected_categories,
            plot_marginals=PLOT_MARGINALS
        )

        return fig, data_for_table

    @app.callback(
        [
            Output("data-table", "data"),
            Output("image-selection", "data"),
        ],
        [
            Input("data-plot", "selectedData"),
            Input("data-plot", "clickData"),
            Input("data-table", "active_cell"),
        ],
        [State("data-table", "data")],
    )
    def display_selected_data_and_image(selectedData, clickData, active_cell, rows_data):
        """Updates the data table and image selection store based on plot or table interaction."""
        DF = state.DF
        ctx = callback_context

        if not ctx.triggered:
            return no_update, {}

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        store_out = {}

        if triggered_id == "data-plot" and selectedData:
            # BUG FIX: Added check for customdata existence to handle histogram selections gracefully
            original_indices = [
                point["customdata"][0] for point in selectedData["points"] if "customdata" in point
            ]

            selected_rows = DF.loc[DF["id"].isin(original_indices)]

            if not selected_rows.empty:
                store_out = selected_rows.iloc[0][
                    ["relative_filepath"]
                ].to_dict()

                table_data = selected_rows.to_dict("records")
                state.selected_rows_global = table_data

                return table_data, store_out

        elif triggered_id == "data-table" and active_cell and rows_data:
            row = rows_data[active_cell["row"]]
            store_out = {
                "relative_filepath": row["relative_filepath"],
            }
            return no_update, store_out

        return no_update, {}

def register_image_callbacks(app: Dash, state, socketio):
    """
    Registers callbacks for image display and downloading.

    Args:
        app (Dash): The Dash application instance.
        state (AppState): The shared application state.
        socketio (SocketIO): The SocketIO instance.
    """
    @app.callback(
        Output("numpy-container", "children"),
        Input("image-selection", "data"),
        Input('harmonize-checkbox', 'value'),
    )
    def display_numpy_image(data_store_content, harmonize_state):
        """Loads and displays the selected numpy image."""
        ROOT_DIR = state.ROOT_DIR

        if data_store_content and all(
            k in data_store_content for k in ["relative_filepath"]
        ):
            relative_filepath = data_store_content["relative_filepath"]
            full_file_path = os.path.join(ROOT_DIR, relative_filepath)

            socketio.emit("send_file_message", {"file_name": relative_filepath})

            try:
                numpy_array = np.load(full_file_path)
                image_to_display = numpy_array

                state.HARMONIZE = harmonize_state

                if state.HARMONIZE:
                    image_to_display = harmonize_image(image_to_display)

                fig = px.imshow(image_to_display)
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=20, r=20, t=20, b=20),
                )
                return dcc.Graph(figure=fig)

            except Exception as e:
                prerror(f"Failed to load or process numpy file at {full_file_path}: {str(e)}")
                return "Error loading image."

        return "No image selected or file path unavailable."

    @app.callback(
        Output("download-dataset", "data"),
        Input("btn_image", "n_clicks"),
        State("image-selection", "data"),
        prevent_initial_call=True,
    )
    def download_dataset(n_clicks, data_store_content):
        """Initiates download of the selected image file."""
        ROOT_DIR = state.ROOT_DIR
        if data_store_content and "relative_filepath" in data_store_content:
            relative_filepath = data_store_content["relative_filepath"]
            full_file_path = os.path.join(ROOT_DIR, relative_filepath)
            return dcc.send_file(full_file_path)
        else:
            return None

def register_main_callbacks(app: Dash, state, socketio):
    """
    Wrapper to register all main application callbacks.
    """
    register_plot_callbacks(app, state)
    register_image_callbacks(app, state, socketio)
