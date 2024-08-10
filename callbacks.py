import logging
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import Dash, Input, Output, MATCH, State, callback_context
from functions import create_histogram_figure
from dash.exceptions import PreventUpdate
from dash import ALL

def register_numeric_callbacks(app: Dash, DF, all_numeric_options):
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
            # Output("reset-button-store", "data")
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
            # State("number-of-reset-clicks", "data")
        ],
    )
    def update_limits(
        relayoutData, n_clicks, left_limit_state, right_limit_state, id, selected_nums
    ):
        ctx = callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        print(f"Triggered ID: {triggered_id}")
        
        if triggered_id == "reset-button-nums":
            selected_options = [
                option
                for option in all_numeric_options
                if option["label"]
                in [cat["label"] for cat in selected_nums]  # Extract labels
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
                in [cat["label"] for cat in selected_nums]  # Extract labels
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

    @app.callback(
        Output("collapse-feature-graphs", "is_open"),
        [Input("collapse-button-graphs", "n_clicks")],
        [State("collapse-feature-graphs", "is_open")],
    )
    def toggle_collapse(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse-feature-subset", "is_open"),
        [Input("collapse-button-subset", "n_clicks")],
        [State("collapse-feature-subset", "is_open")],
    )
    def toggle_collapse(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse-feature-categories", "is_open"),
        [Input("collapse-button-categories", "n_clicks")],
        [State("collapse-feature-categories", "is_open")],
    )
    def toggle_collapse(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse-axis-dropdowns", "is_open"),
        [Input("collapse-button-axis-dropdowns", "n_clicks")],
        [State("collapse-axis-dropdowns", "is_open")],
    )
    def toggle_collapse(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse-feature-histograms", "is_open"),
        [Input("collapse-button-histograms", "n_clicks")],
        [State("collapse-feature-histograms", "is_open")],
    )
    def toggle_collapse(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open


def register_categorical_callbacks(app: Dash, DF, all_categorical_options):

    logging.info("CAT: Registering categorical callbacks...")
    logging.debug("CAT: All categorical options:")
    logging.debug(all_categorical_options)
    
    # Callback to generate dynamic dropdowns (modified from your old code)
    @app.callback(
        Output("cat-dropdown-container", "children"),
        Input("selected-cats-store", "data"),
    )
    def generate_dynamic_dropdowns(selected_cats):
        # Filter options based on selected_cats
        logging.debug("CAT: All options:")
        logging.debug(all_categorical_options)
        logging.debug("CAT: Selected cats:")
        logging.debug(selected_cats)

        selected_options = [
            option
            for option in all_categorical_options
            if option["label"]
            in [cat["label"] for cat in selected_cats]  # Extract labels
        ]
        logging.debug("Selected options:", selected_options)
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
        logging.debug(dropdowns)
        return dropdowns

    @app.callback(
        Output({'type': 'dynamic-dropdown', 'index': ALL}, 'value'),
        [Input("reset-button", "n_clicks")],
        State("selected-cats-store", "data"),
        prevent_initial_call=True  # Prevent the callback from running at app start
    )
    def reset_dropdowns(n_clicks, selected_cat_options):
        if n_clicks is None:
            # Prevents the callback from firing before any clicks have occurred
            raise PreventUpdate

        logging.info(f"CAT: Resetting categories...")
        reset_values = []
        for option in selected_cat_options:
            # Each dropdown is reset to contain all unique values available for its category
            reset_value = DF[option["value"]].unique().tolist()
            reset_values.append(reset_value)
        
        # Since we're targeting all dropdowns of a certain type, we return a list of reset values
        # The order of values in the list corresponds to the order of dropdowns, which should be
        # consistent if they are generated in a consistent manner elsewhere in the app
        logging.info(f"Reset values: {reset_values}")
        return reset_values

    @app.callback(
        Output("cat-available-container", "data"),  # Update options in the multiselect
        Output(
            "cat-available-container", "value"
        ),  # Update selected options in the multiselect
        Output(
            "selected-cats-store", "data"
        ),  # Update the store for selected categories
        Output("x-axis-dropdown", "options"),
        Output("y-axis-dropdown", "options"),
        Output("color-dropdown", "options"),
        Input({"type": "dynamic-row", "index": ALL}, "value"),
        Input("cat-available-container", "value"),  # User selections in this container
        State("selected-cats-store", "data"),  # Currently stored selections
        State("selected-nums-store", "data"),  # Currently stored selections
    )
    def update_available_categories(dynamic_row, available_values, stored_data, selected_numeric):
        logging.info("CAT: Update available categories callback triggered...")
        if not stored_data:
            stored_data = []  # Initialize if empty

        if dynamic_row:  
            changed_index = [i for i, item in enumerate(dynamic_row) if not item]

            for index in sorted(changed_index, reverse=True):  # Remove in reverse to avoid shifting indices
                label_to_move = stored_data[index]["label"] 
                del stored_data[index]
                available_values.append(label_to_move) 

            available_values.sort()  # Sort after all moves 

        logging.debug("User selections (available_values):")
        logging.debug(available_values)
        logging.debug("Stored data (selected categories):")
        logging.debug(stored_data)

        # Re-calculate available options based on what's currently selected
        # Assuming all_categorical_options is accessible here, containing all possible categories
        available_options = [
            option
            for option in all_categorical_options
            if option["label"] in available_values
        ]
        # The store is now the inverted to that:
        updated_store = [
            option
            for option in all_categorical_options
            if option["label"] not in available_values
        ]

        available_axis_options = updated_store + selected_numeric

        logging.debug("Available options:")
        logging.debug(available_options)
        logging.debug("Available values:")
        logging.debug(available_values)
        logging.debug("Updated store:")
        logging.debug(updated_store)
        return available_options, available_values, updated_store, available_axis_options, available_axis_options, available_axis_options
