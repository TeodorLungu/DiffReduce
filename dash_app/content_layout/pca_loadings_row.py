import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html

from constants import IMAGE_DOWNLOAD_OPTIONS

fig = px.scatter()
fig.update_yaxes(
    scaleanchor="x",
    scaleratio=1,
)


pca_loadings_row = [
    dbc.Row(
        dbc.Col(
            html.H5(
                "PCA Loadings and Correlation Heatmap",
                className="text-center mt-2",
            ),
            width={
                "size": 6,
                "offset": 3,
            },
        ),
    ),
    dbc.Row(
        [
            dbc.Col(
                dcc.Graph(
                    id="graph-pca-loadings",
                    figure=fig,
                    clear_on_unhover=True,
                    style={
                        "height": "600px",
                    },
                    config=IMAGE_DOWNLOAD_OPTIONS,
                ),
                width=6,
            ),
            dbc.Col(
                dcc.Graph(
                    id="graph-correlation-heatmap",
                    figure=fig,
                    clear_on_unhover=True,
                    style={
                        "height": "600px",
                    },
                    config=IMAGE_DOWNLOAD_OPTIONS,
                ),
                width=6,
            ),
        ],
    ),
    dbc.Row(
        dbc.Col(
            html.H5(
                "PCA Explained Variance",
                className="text-center mt-2",
            ),
            width={
                "size": 6,
                "offset": 3,
            },
        ),
    ),
    dbc.Row(
        dbc.Col(
            [
                dcc.Graph(
                    id="graph-explained-variance",
                    style={"height": "600px"},
                ),
            ],
        ),
    ),
    dbc.Row(
        dbc.Col(
            html.H5(
                "SPLOM of Original Measures",
                className="text-center mt-2",
            ),
            width={
                "size": 6,
                "offset": 3,
            },
        ),
    ),
    dbc.Row(
        [
            dbc.Col(
                [
                    dcc.Dropdown(
                        id="original-measures-dropdown",
                        multi=True,
                    ),
                    dbc.Tooltip(
                        "Select the measures to display in the scatter matrix plot.",
                        target="original-measures-dropdown",
                    ),
                ],
                width=5,
            ),
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.Input(
                            id="input-stratified-sampling-2",
                            placeholder="Select Percentage",
                            type="number",
                            pattern="^(100|[1-9][0-9]?)$",
                        ),
                        dbc.InputGroupText("%"),
                        dbc.Tooltip(
                            "Perform stratified sampling based on the given percentage.",
                            target="input-stratified-sampling-2",
                        ),
                    ],
                ),
                width=5,
            ),
            dbc.Col(
                dbc.Button(
                    "Apply Sampling",
                    id="change-splom-button",
                    color="primary",
                ),
                width=2,
            ),
        ]
    ),
    dbc.Row(
        dbc.Col(
            dcc.Graph(
                id="graph-original-measures",
                clear_on_unhover=True,
                style={
                    "height": "1000px",
                },
                config=IMAGE_DOWNLOAD_OPTIONS,
            )
        ),
    ),
]
