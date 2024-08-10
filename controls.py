# Assuming you've modularized your components and this is in layouts.py
from dash import Dash, dcc, html, Input, Output, MATCH, State

import dash_bootstrap_components as dbc
from dash import html

# from components.plots import create_histogram_figure  # Example modularization
from data_loader import DF, numeric_options  # Example import


def get_card_with_plots():
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
            for i, option in enumerate(numeric_options)
        ],
    )
    return card_content
