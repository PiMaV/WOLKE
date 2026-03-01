import dash_bootstrap_components as dbc

import dash_mantine_components as dmc
from dash import (
    dcc,
    html,
    dash_table,
)


def create_layout(
    DF,
    all_categorical_options,
    all_numeric_options,
    selected_categorical_options,
    selected_numeric_options,
    x,
    y,
    color,
    version,
    full_url="http://localhost:8050/",
    token="1234567890",
):
    all_selected_options = selected_categorical_options + selected_numeric_options
    return dbc.Container(
        [  # Main container for Bootstrap layout, now fluid for full width
            dbc.Row(
                [
                    dbc.Col(
                        html.H1(
                            f"WOLKE {version}", className="mb-0"
                        ),  # Remove bottom margin to tighten spacing
                        width=4,
                        align="center",
                    ),
                    dbc.Col(
                        html.H3(
                            "Web-Oriented Layout for Knowledge Exploration",
                            className="mb-0",  # Remove bottom margin for consistent spacing
                        ),
                        width=8,
                    ),
                ],
                justify="center",
                # no_gutters=True,  # Removes gutter spacing between columns for a tighter layout
                className="align-items-center",  # Vertically align items in the middle
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Hr(style={"width": "100%", "borderWidth": "2px"})
                    )  # Adjust style as needed
                ],
                justify="center",
            ),
            dbc.Row(
                [
                    dbc.Col(html.H3("Dataset Size:"), width=4),
                    dbc.Col(
                        dash_table.DataTable(
                            id="info-table",  # Important: You will use this ID to target the table in the callback
                            columns=[
                                {"name": "Category", "id": "Category"},
                                {"name": "Data Points", "id": "Data Points"},
                                {"name": "Percent of Sub.", "id": "Percent"},
                            ],
                            style_as_list_view=True,
                            style_cell={"padding": "5px"},
                            style_header={
                                "backgroundColor": "white",
                                "fontWeight": "bold",
                            },
                        ),
                    ),
                ],
                justify="center",
            ),
            dbc.Row(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.H4(
                                    [
                                        "1.) Start with a ",
                                        html.Span(
                                            "SUBSET. ",
                                            style={
                                                "font-weight": "bold",
                                                "color": "#6f42c1",
                                            },
                                        ),  # Bootstrap primary color for example
                                        "Come back once you filtered properly and increase.",
                                    ],
                                    className="mb-3",
                                    style={
                                        "float": "left",
                                        "margin-right": "20px",
                                    },
                                ),
                                dbc.Button(
                                    "Hide Slider",
                                    id="collapse-button-subset",
                                    color="primary",
                                    className="ml-auto mr-4",  # Keeps the margin to the right of the button
                                    n_clicks=0,
                                ),
                            ],
                            className="d-flex align-items-center",  # Ensures proper alignment of title and button
                        ),
                        dbc.Collapse(
                            dbc.CardBody(
                                [
                                    html.Div(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        html.Label("Subset:"),
                                                        md=2,
                                                        lg=1,
                                                    ),
                                                    dbc.Col(
                                                        dcc.Slider(
                                                            id="subset-range",
                                                            min=0.1,
                                                            max=1,
                                                            step=0.1,
                                                            value=0.2,
                                                        ),
                                                        md=10,
                                                        lg=11,
                                                    ),
                                                ],
                                                align="center",
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            id="collapse-feature-subset",
                            is_open=True,  # Initially shown; toggle to hide/show based on button click
                        ),
                    ],
                )
            ),
            dbc.Row(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.H4(
                                    [
                                        "2.) Select / Filter ",
                                        html.Span(
                                            "CATEGORIES",
                                            style={
                                                "font-weight": "bold",
                                                "color": "#6f42c1",
                                            },
                                        ),
                                        " ",
                                    ],
                                    className="mb-3",
                                    style={
                                        "float": "left",
                                        "margin-right": "20px",
                                    },
                                ),
                                dbc.Button(
                                    "Hide Categories",
                                    id="collapse-button-categories",
                                    color="primary",
                                    className="ml-auto mr-4",  # Keeps the margin to the right of the button
                                    n_clicks=0,
                                ),
                            ],
                            className="d-flex align-items-center",  # Ensures proper alignment of title and button
                        ),
                        dbc.Collapse(
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Div(
                                                    "Each items can be selected individually by clicking x, or all at once (the x to the right) to clear all. This way you can add and remove items. The yellow Reset Button will set everything back to the initial state.",
                                                    style={
                                                        "font-size": "1.0rem",
                                                        # "font-weight": "bold",
                                                        "display": "flex",
                                                        "align-items": "center",  # Vertically centers the text in the div
                                                        "justify-content": "flex-start",  # Aligns text to the start of the div
                                                    },
                                                ),
                                                width=9,
                                            ),
                                            dbc.Col(
                                                dbc.Button(
                                                    "Reset Categories",
                                                    id="reset-button",
                                                    n_clicks=0,
                                                    color="warning",
                                                ),
                                                width=3,
                                                style={
                                                    "display": "flex",
                                                    "align-items": "center",  # Aligns the button vertically in the center
                                                    "justify-content": "flex-end",  # Aligns the button to the end (right)
                                                },
                                            ),
                                        ],
                                        className="align-items-center",  # This should ensure that the row itself aligns items in the center vertically
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Hr(
                                                    style={
                                                        "width": "100%",
                                                        "borderWidth": "2px",
                                                    }
                                                )
                                            )  # Adjust style as needed
                                        ],
                                        justify="center",
                                    ),
                                    dbc.Row(
                                        [
                                            html.Div(
                                                "Additional available Categories (click x to show them as category):",
                                                style={
                                                    "font-size": "1.2rem",
                                                    "font-weight": "bold",
                                                    "display": "flex",
                                                    "align-items": "center",  # Vertically centers the text in the div
                                                    "justify-content": "flex-start",  # Aligns text to the start of the div
                                                },
                                            ),
                                        ],
                                        justify="center",
                                    ),
                                    dbc.Row(
                                        create_multi_select_with_available_categories(
                                            selected_categorical_options,
                                            all_categorical_options,
                                        ),
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Hr(
                                                    style={
                                                        "width": "100%",
                                                        "borderWidth": "2px",
                                                    }
                                                )
                                            )  # Adjust style as needed
                                        ],
                                        justify="center",
                                    ),
                                    # html.Div(id='intermediate-value', style={'display': 'none'}),
                                    dbc.Row(
                                        dbc.Col(html.Div(id="cat-dropdown-container")),
                                    ),
                                ]
                            ),
                            id="collapse-feature-categories",
                            is_open=True,  # Initially shown; toggle to hide/show based on button click
                        ),
                    ],
                )
            ),
            dbc.Row(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.H4(
                                    [
                                        "3.) Select ",
                                        html.Span(
                                            "NUMERICAL",
                                            style={
                                                "font-weight": "bold",
                                                "color": "#6f42c1",
                                            },
                                        ),  # Bootstrap primary color for example
                                        " ",
                                        html.Span(
                                            "RANGES",
                                            style={
                                                "font-weight": "bold",
                                                "color": "#6f42c1",
                                            },
                                        ),  # Bootstrap primary color for example
                                        "",
                                    ],
                                    className="mb-3",
                                    style={
                                        "float": "left",
                                        "margin-right": "20px",
                                    },
                                ),
                                dbc.Button(
                                    "Hide Histograms",
                                    id="collapse-button-histograms",
                                    color="primary",
                                    className="ml-auto mr-4",  # Keeps the margin to the right of the button
                                    n_clicks=0,
                                ),
                            ],
                            className="d-flex align-items-center",  # Ensures proper alignment of title and button
                        ),
                        dbc.Collapse(
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Div(
                                                    "Select Ranges by dragging on the histogram, or use the textboxes to define values. Doubleclick into a histogram to reset the value range. Click the yellow Reset Button to reset all ranges.",
                                                    style={
                                                        "font-size": "1.0rem",
                                                        # "font-weight": "bold",
                                                        "display": "flex",
                                                        "align-items": "center",  # Vertically centers the text in the div
                                                        "justify-content": "flex-start",  # Aligns text to the start of the div
                                                    },
                                                ),
                                                width=9,
                                            ),
                                            dbc.Col(
                                                dbc.Button(
                                                    "Reset Ranges",
                                                    id="reset-button-nums",
                                                    n_clicks=0,
                                                    color="warning",
                                                ),
                                                width=3,
                                                style={
                                                    "display": "flex",
                                                    "align-items": "center",  # Aligns the button vertically in the center
                                                    "justify-content": "flex-end",  # Aligns the button to the end (right)
                                                },
                                            ),
                                        ],
                                        className="align-items-center",  # This should ensure that the row itself aligns items in the center vertically
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Hr(
                                                    style={
                                                        "width": "100%",
                                                        "borderWidth": "2px",
                                                    }
                                                )
                                            )  # Adjust style as needed
                                        ],
                                        justify="center",
                                    ),
                                    dbc.Row(
                                        create_hist_range(selected_numeric_options, DF)
                                    ),
                                ]
                            ),
                            id="collapse-feature-histograms",
                            is_open=True,  # Initially shown; toggle to hide/show based on button click
                        ),
                    ],
                )
            ),
            dbc.Row(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.H4(
                                    [
                                        "4.) Select ",
                                        html.Span(
                                            "AXES ",
                                            style={
                                                "font-weight": "bold",
                                                "color": "#6f42c1",
                                            },
                                        ),
                                        "for the Plot",
                                    ],
                                    className="mb-3",
                                    style={
                                        "float": "left",
                                        "margin-right": "20px",
                                    },
                                ),
                                dbc.Button(
                                    "Hide Dropdowns",
                                    id="collapse-button-axis-dropdowns",
                                    color="primary",
                                    className="ml-auto mr-4",  # Keeps the margin to the right of the button
                                    n_clicks=0,
                                ),
                            ],
                            className="d-flex align-items-center",  # Ensures proper alignment of title and button
                        ),
                        dbc.Collapse(
                            dbc.CardBody(
                                [
                                    create_axis_dropdowns(
                                        all_selected_options, x, y, color
                                    )
                                ]
                            ),
                            id="collapse-axis-dropdowns",
                            is_open=True,
                        ),
                    ],
                )
            ),
            dbc.Row(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                html.H4(
                                    [
                                        "5.) ",
                                        html.Span(
                                            "EXPLORE ",
                                            style={
                                                "font-weight": "bold",
                                                "color": "#6f42c1",
                                            },
                                        ),
                                        "Your Data: Zoom, Drag, and Discover Details on Hover",
                                    ],
                                    className="graphs-card",
                                    id="graphs-card",
                                    style={
                                        "float": "left",
                                        "margin-right": "20px",  # Increased right margin for spacing
                                    },
                                ),
                                dbc.Button(
                                    "Hide Graphs",
                                    id="collapse-button-graphs",  # Ensure this ID is unique
                                    color="primary",
                                    className="ml-auto mr-4",  # Keeps the margin to the right of the button
                                    n_clicks=0,
                                ),
                                dbc.Tooltip(
                                    [
                                        html.Div(
                                            [
                                                html.H4(
                                                    "Explore Your Data:",
                                                    style={
                                                        "fontSize": "1.25rem",
                                                        "marginBottom": "10px",
                                                    },
                                                ),  # Larger header
                                                html.P(
                                                    "Double-click to reset.",
                                                    style={"textAlign": "left"},
                                                ),
                                                html.P(
                                                    "Click on a point to see details, click again to go back.",
                                                    style={"textAlign": "left"},
                                                ),
                                                html.P(
                                                    "Use the box or lasso select tool to select multiple points.",
                                                    style={"textAlign": "left"},
                                                ),
                                                html.P(
                                                    "Explore the rest of the graph using the buttons on the top right.",
                                                    style={"textAlign": "left"},
                                                ),
                                            ],
                                            # style={"width": "400px"},
                                        )  # Encapsulate all in a Div to control maxWidth
                                    ],
                                    target="graphs-card",  # Matches the ID of the target element
                                    placement="auto",
                                    style={
                                        "width": 400,  # Ensure this is lowercase
                                        "max-width": 400,  # Also set maxWidth to ensure it takes effect
                                    },
                                ),
                            ],
                            className="d-flex align-items-center",  # Ensures proper alignment of title and button
                        ),
                        dbc.Collapse(
                            dbc.CardBody(
                                [
                                    html.Div(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        dcc.Loading(
                                                            id="graph-loading",
                                                            type="default",  # You can choose "circle", "cube", "dot", etc.
                                                            overlay_style={
                                                                "visibility": "visible",
                                                                "filter": "blur(1px)",
                                                            },
                                                            children=dcc.Graph(
                                                                id="data-plot",
                                                                style={
                                                                    "minHeight": "800px"
                                                                },
                                                            ),
                                                        ),
                                                        width=12,
                                                        lg=11,
                                                        xl=11,
                                                        className="mx-auto mb-2",
                                                    ),
                                                ],
                                                align="center",
                                                className="mb-2",
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        html.Div(
                                                            id="numpy-container",
                                                            children="Image will be displayed here",
                                                        ),
                                                        width=12,
                                                        lg=11,
                                                        xl=11,
                                                        className="mx-auto mb-2",
                                                    ),
                                                ],
                                                align="center",
                                                className="mb-2",
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        html.Button(
                                                            "Download Dataset",
                                                            id="btn_image",
                                                        ),
                                                        width={"size": 3, "offset": 0},
                                                        className="text-center mb-2",
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.Label("URL for BLITZ"),
                                                            dbc.Input(
                                                                type="text",
                                                                id="url_input",
                                                                value=full_url,
                                                            ),
                                                        ],
                                                        width=3,
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.Label("TOKEN"),
                                                            dbc.Input(
                                                                type="text",
                                                                id="token_input",
                                                                value=token,
                                                            ),
                                                        ],
                                                        width=3,
                                                    ),
                                                    dbc.Col(
                                                        dbc.Checkbox(
                                                            id="normalize-checkbox",
                                                            label="Normalize Image",
                                                            style={
                                                                "margin-top": "10px"
                                                            },
                                                        ),
                                                        width={"size": 3, "offset": 0},
                                                    ),
                                                ],
                                                align="center",
                                                className="mb-2",
                                            ),
                                            dbc.Tooltip(
                                                "Adjust image intensities by clipping values to mean ± 3 standard deviations (with a lower bound of 0).",
                                                id="tooltip_harmo",
                                                target="harmonize-checkbox",
                                            ),
                                            dcc.Store(
                                                id="normalize-state-store",
                                                data={"normalize": False},
                                            ),
                                            dcc.Download(id="download-dataset"),
                                            dbc.Tooltip(
                                                "Download Dataset from Server for local use.",
                                                id="tooltip_button",
                                                target="btn_image",
                                            ),
                                            dbc.Row(
                                                dash_table.DataTable(
                                                    id="data-table",
                                                    columns=[
                                                        {
                                                            "name": i,
                                                            "id": i,
                                                            "selectable": True,
                                                        }
                                                        for i in DF.columns
                                                    ],
                                                    page_size=20,
                                                    style_table={
                                                        "height": "300px",
                                                        "overflowY": "auto",
                                                    },
                                                    filter_action="native",
                                                    sort_action="native",
                                                    selected_rows=[0],
                                                    export_format="csv",
                                                    export_headers="display",
                                                ),
                                                className="mb-2",
                                            ),
                                            dbc.Tooltip(
                                                "Select a cell to reload the image.",
                                                id="tooltip_table",
                                                target="data-table",
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            id="collapse-feature-graphs",
                            is_open=True,
                        ),
                    ],
                )
            ),
            dcc.Store(id="image-selection"),
            dcc.Interval(id="viewer-sync-interval", interval=1500),
            dcc.Store(id="shared-selection-state", data={}),
            dcc.Store(id="selected-cats-store", data=selected_categorical_options),
            dcc.Store(id="selected-nums-store", data=selected_numeric_options),
            # dcc.Store(id="number-of-reset-clicks", data=0),
            # print('Selected Categorical Options:', selected_categorical_options),
        ],
        fluid=True,
    )


def create_hist_range(selected_numeric_options, DF):
    card_content = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            id={"type": "histogram-graph", "index": i},
                            style={"height": "100px"},
                            config={"displayModeBar": False},  # Disable the modebar
                        ),
                        width=10,  # Plot takes up 10 columns
                    ),
                    dbc.Col(  # This column contains the "min" and "max" inputs, each preceded by its label
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            "Min:",
                                            style={
                                                "margin-right": "5px",
                                                "display": "inline-block",
                                            },
                                        ),  # Label for the min input box
                                        dcc.Input(
                                            id={"type": "left-limit", "index": i},
                                            type="number",
                                            debounce=True,
                                            value=DF[option["value"]].min(),
                                            style={
                                                "width": "80px",
                                                "display": "inline-block",
                                            },  # Adjusted width and display
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "marginBottom": "10px",
                                    },  # Ensure label and input are on the same line
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            "Max:",
                                            style={
                                                "margin-right": "5px",
                                                "display": "inline-block",
                                            },
                                        ),  # Label for the max input box
                                        dcc.Input(
                                            id={"type": "right-limit", "index": i},
                                            type="number",
                                            debounce=True,
                                            value=DF[option["value"]].max(),
                                            style={
                                                "width": "80px",
                                                "display": "inline-block",
                                            },  # Adjusted width and display
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                    },  # Ensure label and input are on the same line
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flexDirection": "column",
                                "justifyContent": "center",
                            },  # Vertically center the inputs within the column
                        ),
                        width=2,  # Input boxes take up 2 columns
                    ),
                ],
                className="mb-1 align-items-center",  # Adds vertical alignment to center
            )
            for i, option in enumerate(selected_numeric_options)
        ],
    )
    return card_content


def create_axis_dropdowns(
    all_options, x, y, color, z=None, x_marginal=None, y_marginal=None
):
    card_content = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("X", className="dropdown-label"),
                            dcc.Dropdown(
                                id="x-axis-dropdown",
                                options=all_options,
                                value=x,
                                placeholder="Select X",
                                clearable=False,
                            ),
                            html.Label(
                                "X Marginal",
                                className="dropdown-label",
                                style={"marginTop": "10px"},
                            ),
                            dcc.Dropdown(
                                id="x-marginal-dropdown",
                                options=[
                                    {"label": "Off", "value": "off"},
                                    {"label": "Histogram", "value": "histogram"},
                                    {"label": "Violin", "value": "violin"},
                                ],
                                value=x_marginal or "off",
                                clearable=False,
                            ),
                        ],
                        width=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("Y", className="dropdown-label"),
                            dcc.Dropdown(
                                id="y-axis-dropdown",
                                options=all_options,
                                value=y,
                                placeholder="Select Y",
                                clearable=False,
                            ),
                            html.Label(
                                "Y Marginal",
                                className="dropdown-label",
                                style={"marginTop": "10px"},
                            ),
                            dcc.Dropdown(
                                id="y-marginal-dropdown",
                                options=[
                                    {"label": "Off", "value": "off"},
                                    {"label": "Histogram", "value": "histogram"},
                                    {"label": "Violin", "value": "violin"},
                                ],
                                value=y_marginal or "off",
                                clearable=False,
                            ),
                        ],
                        width=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("Z", className="dropdown-label"),
                            dcc.Dropdown(
                                id="z-axis-dropdown",
                                options=all_options,
                                value=z,
                                placeholder="Select Z",
                                clearable=True,
                            ),
                        ],
                        width=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("Color", className="dropdown-label"),
                            dcc.Dropdown(
                                id="color-dropdown",
                                options=all_options,
                                value=color,
                                placeholder="Select Color",
                                clearable=False,
                            ),
                        ],
                        width=3,
                    ),
                ],
                className="mb-2",
            )
        ],
    )
    return card_content


def create_multi_select_with_available_categories(selected_categorical_options, all_categorical_options):
    # Invert selected_categorical_options with respect to all_categorical_options.
    # We assume that both are lists of dictionaries with "value" and "label" keys.
    inverted_options = [
        option for option in all_categorical_options if option not in selected_categorical_options
    ]
    
    # If needed, ensure each option is in the proper format (here we assume they are already)
    # For example, if they were strings, you could convert like:
    # inverted_options = [{"value": str(opt), "label": str(opt)} for opt in inverted_options]

    return dbc.Col(
        dmc.MultiSelect(
            id="cat-available-container",
            data=inverted_options,  # Data must be in the format: [{"value": ..., "label": ...}, ...]
            value=[],  # No options selected by default
            searchable=True,
            clearable=True,
            placeholder=("No additional categories available" if not inverted_options else "Select categories"),
        ),
    )

