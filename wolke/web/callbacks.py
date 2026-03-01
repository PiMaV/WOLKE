"""
Register all Dash callbacks. Uses state (no globals) and receives options/plot_generator/socketio.
"""
import logging
import os
from typing import Any

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import ALL, MATCH, Dash, dcc, Input, Output, State, callback_context, no_update
from dash.exceptions import PreventUpdate

from wolke.utils import (
    create_histogram_figure,
    load_image_as_array,
    normalize_image,
    prdebug,
    prerror,
    prinfo,
    prwarn,
    sort_categories,
)

logger = logging.getLogger(__name__)


def register_numeric_callbacks(
    app: Dash,
    df: pd.DataFrame,
    all_numeric_options: list[dict[str, str]],
) -> None:
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
            o for o in all_numeric_options
            if o["label"] in [c["label"] for c in (selected_nums or [])]
        ]
        index = id["index"]
        column_name = selected_options[index]["label"]
        fig = create_histogram_figure(df, column_name)
        fig.update_layout(xaxis_range=[left_limit, right_limit])
        return fig

    @app.callback(
        [
            Output({"type": "left-limit", "index": MATCH}, "value"),
            Output({"type": "right-limit", "index": MATCH}, "value"),
        ],
        [
            Input({"type": "histogram-graph", "index": MATCH}, "relayoutData"),
            Input("reset-button-nums", "n_clicks"),
        ],
        [
            State({"type": "left-limit", "index": MATCH}, "value"),
            State({"type": "right-limit", "index": MATCH}, "value"),
            State({"type": "histogram-graph", "index": MATCH}, "id"),
            State("selected-nums-store", "data"),
        ],
    )
    def update_limits(relayoutData, n_clicks, left_limit_state, right_limit_state, id, selected_nums):
        ctx = callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if triggered_id == "reset-button-nums":
            selected_options = [
                o for o in all_numeric_options
                if o["label"] in [c["label"] for c in (selected_nums or [])]
            ]
            index = id["index"]
            col = selected_options[index]["value"]
            return df[col].min(), df[col].max()
        if relayoutData and (
            "autosize" in relayoutData
            or ("xaxis.range[0]" not in relayoutData and "xaxis.range[1]" not in relayoutData)
        ):
            selected_options = [
                o for o in all_numeric_options
                if o["label"] in [c["label"] for c in (selected_nums or [])]
            ]
            index = id["index"]
            col = selected_options[index]["value"]
            return df[col].min(), df[col].max()
        if relayoutData and "xaxis.range[0]" in relayoutData and "xaxis.range[1]" in relayoutData:
            return float(relayoutData["xaxis.range[0]"]), float(relayoutData["xaxis.range[1]"])
        return left_limit_state, right_limit_state


def register_collapse_button_callbacks(app: Dash) -> None:
    pairs = [
        ("collapse-feature-graphs", "collapse-button-graphs"),
        ("collapse-feature-subset", "collapse-button-subset"),
        ("collapse-feature-categories", "collapse-button-categories"),
        ("collapse-axis-dropdowns", "collapse-button-axis-dropdowns"),
        ("collapse-feature-histograms", "collapse-button-histograms"),
    ]

    def _make_toggle(out_id: str, btn_id: str):
        @app.callback(
            Output(out_id, "is_open"),
            [Input(btn_id, "n_clicks")],
            [State(out_id, "is_open")],
        )
        def _toggle(n_clicks, is_open):
            return not is_open if n_clicks else is_open

    for out_id, btn_id in pairs:
        _make_toggle(out_id, btn_id)


def register_categorical_callbacks(
    app: Dash,
    df: pd.DataFrame,
    all_categorical_options: list[dict[str, str]],
) -> None:
    @app.callback(
        Output("cat-dropdown-container", "children"),
        Input("selected-cats-store", "data"),
    )
    def generate_dynamic_dropdowns(selected_cats):
        selected_options = [
            o for o in all_categorical_options
            if o["label"] in [c["label"] for c in (selected_cats or [])]
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
                            data=[{"label": c, "value": c} for c in df[option["value"]].unique()],
                            value=df[option["value"]].unique().tolist(),
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
        Output({"type": "dynamic-dropdown", "index": ALL}, "value"),
        Input("reset-button", "n_clicks"),
        State("selected-cats-store", "data"),
        prevent_initial_call=True,
    )
    def reset_dropdowns(n_clicks, selected_cat_options):
        if n_clicks is None:
            raise PreventUpdate
        return [df[o["value"]].unique().tolist() for o in (selected_cat_options or [])]

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
        if not stored_data:
            stored_data = []
        av = list(available_values) if available_values else []
        if dynamic_row:
            changed_index = [i for i, item in enumerate(dynamic_row) if not item]
            for index in sorted(changed_index, reverse=True):
                label_to_move = stored_data[index]["label"]
                del stored_data[index]
                av.append(label_to_move)
            av.sort()
        available_options = [
            o for o in all_categorical_options if o["label"] in av
        ]
        updated_store = [
            o for o in all_categorical_options if o["label"] not in av
        ]
        axis_opts = updated_store + (selected_numeric or [])
        return available_options, av, updated_store, axis_opts, axis_opts, axis_opts


def register_data_and_plot_callbacks(
    app: Dash,
    state: Any,
    plot_generator: Any,
    selected_numeric_options: list[dict[str, str]],
) -> None:
    """Register update_dataframe, display_selected_data_and_image, display_numpy_image, download."""
    df = state.df
    rel_col = state.relative_filepath_column
    base_dir = state.image_base_dir

    @app.callback(
        [Output("data-plot", "figure"), Output("info-table", "data")],
        State("selected-cats-store", "data"),
        [
            Input("subset-range", "value"),
            Input("x-axis-dropdown", "value"),
            Input("y-axis-dropdown", "value"),
            Input("color-dropdown", "value"),
            Input("z-axis-dropdown", "value"),
            Input("x-marginal-dropdown", "value"),
            Input("y-marginal-dropdown", "value"),
            Input({"type": "left-limit", "index": ALL}, "value"),
            Input({"type": "right-limit", "index": ALL}, "value"),
            Input({"type": "dynamic-dropdown", "index": ALL}, "value"),
        ],
    )
    def update_dataframe(
        selected_cat_options,
        subsample_ratio,
        x_column_name,
        y_column_name,
        cluster_column_name,
        z_column_name,
        marginal_x,
        marginal_y,
        all_left_limits,
        all_right_limits,
        dropdown_values,
    ):
        if not subsample_ratio:
            raise PreventUpdate
        if not x_column_name and selected_numeric_options:
            x_column_name = selected_numeric_options[0]["label"]
        if not y_column_name and selected_numeric_options:
            y_column_name = selected_numeric_options[1]["label"] if len(selected_numeric_options) > 1 else selected_numeric_options[0]["label"]
        if not cluster_column_name and selected_numeric_options:
            cluster_column_name = selected_numeric_options[0]["label"]
        if not cluster_column_name and selected_cat_options:
            cluster_column_name = selected_cat_options[0]["value"]
        if not x_column_name or not y_column_name:
            raise PreventUpdate
        if not cluster_column_name:
            cluster_column_name = x_column_name
        try:
            _fig, _tbl = _update_dataframe_impl(
                df, selected_numeric_options, selected_cat_options,
                subsample_ratio, x_column_name, y_column_name, cluster_column_name,
                z_column_name, marginal_x, marginal_y,
                all_left_limits, all_right_limits, dropdown_values,
                plot_generator,
            )
            return _fig, _tbl
        except Exception as e:
            logger.exception("update_dataframe failed: %s", e)
            empty_fig = px.scatter(x=[], y=[]).update_layout(height=800)
            empty_table = [
                {"Category": "Original", "Data Points": 0, "Percent": "-"},
                {"Category": "Subsampled", "Data Points": 0, "Percent": "-"},
                {"Category": "Filtered", "Data Points": 0, "Percent": "-"},
            ]
            return empty_fig, empty_table

    def _update_dataframe_impl(
        df, selected_numeric_options, selected_cat_options,
        subsample_ratio, x_column_name, y_column_name, cluster_column_name,
        z_column_name, marginal_x, marginal_y,
        all_left_limits, all_right_limits, dropdown_values,
        plot_generator,
    ):
        selected_cats = selected_cat_options or []
        df_filtered = df.sample(frac=subsample_ratio, random_state=42)
        sub_shape = df_filtered.shape
        if dropdown_values and len(dropdown_values) == len(selected_cats):
            for dropdown_value, option in zip(dropdown_values, selected_cats):
                col = option["value"]
                if dropdown_value is not None:
                    vals = dropdown_value if isinstance(dropdown_value, (list, tuple)) else [dropdown_value]
                    df_filtered = df_filtered[df_filtered[col].isin(vals)]
        # Numeric limits: use from inputs if available, else full range (initial load)
        n_num = len(selected_numeric_options)
        left_limits = list(all_left_limits) if all_left_limits and len(all_left_limits) >= n_num else []
        right_limits = list(all_right_limits) if all_right_limits and len(all_right_limits) >= n_num else []
        if len(left_limits) < n_num or len(right_limits) < n_num:
            left_limits = [float(df[o["value"]].min()) for o in selected_numeric_options]
            right_limits = [float(df[o["value"]].max()) for o in selected_numeric_options]
        for index, option in enumerate(selected_numeric_options):
            col = option["value"]
            if col not in df_filtered.columns:
                continue
            left, right = left_limits[index], right_limits[index]
            if left is not None and right is not None:
                df_filtered = df_filtered[(df_filtered[col] >= left) & (df_filtered[col] <= right)]
        selected_categories = []
        if x_column_name in df_filtered.columns:
            if pd.api.types.is_numeric_dtype(df[x_column_name]):
                x_index = next(
                    (i for i, o in enumerate(selected_numeric_options) if o["label"] == x_column_name),
                    None,
                )
                if x_index is not None:
                    df_filtered = df_filtered[
                        (df_filtered[x_column_name] >= left_limits[x_index])
                        & (df_filtered[x_column_name] <= right_limits[x_index])
                    ]
            else:
                selected_categories = sort_categories(df, x_column_name, df_filtered)
                df_filtered = df_filtered[df_filtered[x_column_name].isin(selected_categories)]
        if y_column_name in df_filtered.columns:
            if pd.api.types.is_numeric_dtype(df[y_column_name]):
                y_index = next(
                    (i for i, o in enumerate(selected_numeric_options) if o["label"] == y_column_name),
                    None,
                )
                if y_index is not None:
                    df_filtered = df_filtered[
                        (df_filtered[y_column_name] >= left_limits[y_index])
                        & (df_filtered[y_column_name] <= right_limits[y_index])
                    ]
            else:
                selected_categories = sort_categories(df, y_column_name, df_filtered)
                df_filtered = df_filtered[df_filtered[y_column_name].isin(selected_categories)]
        if cluster_column_name in df_filtered.columns:
            if pd.api.types.is_numeric_dtype(df[cluster_column_name]):
                ci = next(
                    (i for i, o in enumerate(selected_numeric_options) if o["label"] == cluster_column_name),
                    None,
                )
                if ci is not None:
                    df_filtered = df_filtered[
                        (df_filtered[cluster_column_name] >= left_limits[ci])
                        & (df_filtered[cluster_column_name] <= right_limits[ci])
                    ]
            else:
                selected_categories = sort_categories(df, cluster_column_name, df_filtered)
                df_filtered = df_filtered[df_filtered[cluster_column_name].isin(selected_categories)]
        n_orig, n_sub, n_filt = df.shape[0], sub_shape[0], df_filtered.shape[0]
        percent_org = (n_orig / n_sub) * 100
        percent_filt = (n_filt / n_sub) * 100
        data_for_table = [
            {"Category": "Original", "Data Points": n_orig, "Percent": f"{percent_org:.1f}%"},
            {"Category": "Subsampled", "Data Points": n_sub, "Percent": "-"},
            {"Category": "Filtered", "Data Points": n_filt, "Percent": f"{percent_filt:.1f}%"},
        ]
        if marginal_x == "off":
            marginal_x = None
        if marginal_y == "off":
            marginal_y = None
        fig = plot_generator.generate_plot(
            df_filtered,
            x_column_name,
            y_column_name,
            cluster_column_name,
            selected_categories,
            z_column_name,
            marginal_x,
            marginal_y,
        )
        return fig, data_for_table

    @app.callback(
        [Output("data-table", "data"), Output("image-selection", "data")],
        [
            Input("data-plot", "selectedData"),
            Input("data-plot", "clickData"),
            Input("data-table", "active_cell"),
        ],
        [State("data-table", "data"), State("data-plot", "figure")],
    )
    def display_selected_data_and_image(selectedData, clickData, active_cell, rows_data, figure_data):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, {}
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        store_out = {}
        point_indices = []
        if triggered_id == "data-plot":
            if (
                clickData
                and "points" in clickData
                and len(clickData["points"]) > 0
                and clickData["points"][0].get("z") is not None
            ):
                point_indices = [clickData["points"][0]["pointNumber"]]
            elif selectedData and "points" in selectedData and len(selectedData["points"]) > 0:
                point_indices = [p["pointNumber"] for p in selectedData["points"]]
            elif clickData and "points" in clickData and len(clickData["points"]) > 0:
                point_indices = [clickData["points"][0]["pointNumber"]]
            else:
                return no_update, {}
        elif triggered_id == "data-table" and active_cell and rows_data:
            row_index = active_cell["row"]
            row = rows_data[row_index]
            store_out = {rel_col: row[rel_col]}
            if "image_number" in row:
                store_out["image_number"] = row["image_number"]
            state.selected_rows = rows_data
            _socketio = getattr(app.server, "_wolke_socketio", None)
            sync_idx = getattr(state, "_sync_table_index", None)
            if sync_idx is not None:
                if row_index != sync_idx:
                    return no_update, store_out
                state._sync_table_index = None
            if _socketio:
                if len(rows_data) > 1:
                    _socketio.emit("send_file_message", {"file_name": "__selection__.npy", "index": row_index})
                else:
                    _socketio.emit("send_file_message", {"file_name": row[rel_col]})
            return no_update, store_out
        if not point_indices:
            return no_update, {}
        try:
            custom = figure_data.get("data", [{}])[0].get("customdata")
            if custom is None:
                return no_update, {}
            if isinstance(custom, dict) and "_inputArray" in custom:
                original_ids = [custom["_inputArray"][idx]["0"] for idx in point_indices]
            else:
                return no_update, {}
        except Exception as e:
            prwarn(f"Error retrieving customdata: {e}")
            return no_update, {}
        selected_rows = df.loc[df["id"].isin(original_ids)]
        if selected_rows.empty:
            return no_update, {}
        store_out = selected_rows.iloc[0][[rel_col]].to_dict()
        if "image_number" in selected_rows.columns:
            store_out["image_number"] = selected_rows.iloc[0]["image_number"]
        table_data = selected_rows.to_dict("records")
        state.selected_rows = table_data
        _socketio = getattr(app.server, "_wolke_socketio", None)
        if _socketio and table_data:
            current_ids = tuple(r.get("id", i) for i, r in enumerate(table_data))
            last_ids = getattr(state, "_last_emitted_selection_ids", None)
            if current_ids != last_ids:
                state._last_emitted_selection_ids = current_ids
                if len(table_data) == 1:
                    _socketio.emit("send_file_message", {"file_name": table_data[0][rel_col]})
                else:
                    _socketio.emit("send_file_message", {"file_name": "__selection__.npy"})
        return table_data, store_out

    # Store socketio on app.server for use in callback (Dash pattern)
    _socketio = getattr(app.server, "_wolke_socketio", None)

    @app.callback(
        Output("data-table", "active_cell"),
        Input("viewer-sync-interval", "n_intervals"),
        State("data-table", "data"),
    )
    def sync_table_to_viewer_index(n_intervals, table_data):
        """When BLITZ sends viewer_index, set table selection to that row (Contract: viewer_index)."""
        idx = getattr(state, "viewer_index", None)
        if idx is None:
            state._sync_table_index = None
            return no_update
        rows = table_data or []
        if not rows or idx < 0 or idx >= len(rows):
            state.viewer_index = None
            return no_update
        state.viewer_index = None
        state._sync_table_index = idx
        return {"row": idx, "column": 0}

    @app.callback(
        Output("numpy-container", "children"),
        Input("image-selection", "data"),
        Input("normalize-checkbox", "value"),
    )
    def display_numpy_image(data_store_content, normalize_state):
        if not data_store_content or rel_col not in data_store_content:
            return "No image selected or file path unavailable."
        relative_filepath = data_store_content[rel_col]
        full_file_path = os.path.join(base_dir, relative_filepath)
        state.normalize_images = bool(normalize_state)
        try:
            numpy_array = load_image_as_array(full_file_path)
            if numpy_array.ndim == 3 and numpy_array.shape[-1] not in (3, 4):
                image_number = data_store_content.get("image_number", 0)
                image_to_display = numpy_array[image_number]
            else:
                image_to_display = numpy_array
            if normalize_state:
                image_to_display = normalize_image(image_to_display)
            fig = px.imshow(image_to_display)
            fig.update_layout(autosize=True, margin=dict(l=20, r=20, t=20, b=20))
            return dcc.Graph(figure=fig)
        except Exception as e:
            prerror(f"Failed to load image: {e}")
            return "Error loading image."

    @app.callback(
        Output("download-dataset", "data"),
        Input("btn_image", "n_clicks"),
        State("image-selection", "data"),
        prevent_initial_call=True,
    )
    def download_file(n_clicks, data_store_content):
        if not data_store_content or rel_col not in data_store_content:
            return None
        return dcc.send_file(os.path.join(base_dir, data_store_content[rel_col]))


def register_callbacks(
    app: Dash,
    state: Any,
    plot_generator: Any,
    socketio: Any,
    all_categorical_options: list[dict[str, str]],
    all_numeric_options: list[dict[str, str]],
    selected_categorical_options: list[dict[str, str]],
    selected_numeric_options: list[dict[str, str]],
) -> None:
    app.server._wolke_socketio = socketio
    register_numeric_callbacks(app, state.df, all_numeric_options)
    register_collapse_button_callbacks(app)
    register_categorical_callbacks(app, state.df, all_categorical_options)
    register_data_and_plot_callbacks(app, state, plot_generator, selected_numeric_options)
