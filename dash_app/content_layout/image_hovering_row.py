import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

image_hovering = [
    dbc.Row(
        dbc.Col(
            html.H5(
                "Hover over a category to see the image",
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
                        id="image-view-axis-dropdown",
                        options=[
                            "Axial Inferior",
                            "Axial Superior",
                            "Coronal Anterior",
                            "Coronal Posterior",
                            "Sagittal Left",
                            "Sagittal Right",
                        ],
                        value="Axial Superior",
                        multi=False,
                        className="dbc",
                    ),
                    dbc.Tooltip(
                        'Select image view axis. This will update the currently hovered and previously clicked images with the new axis. This can also be used to update the images plotted on the 2D plot, if the "Load Image Markers" switch is refreshed.',
                        target="image-view-axis-dropdown",
                    ),
                ],
                width=2,
            ),
            dbc.Col(
                [
                    dcc.Markdown(
                        "Image for previously clicked category",
                        style={"textAlign": "center"},
                    ),
                    html.Img(
                        id="left-image",
                        src="",
                        style={
                            "width": "300px",
                            "display": "block",
                            "marginLeft": "auto",
                            "marginRight": "auto",
                        },
                    ),
                ],
                width=5,
                style={"textAlign": "center"},
            ),
            dbc.Col(
                [
                    dcc.Markdown(
                        "Image for currently hovered category",
                        style={"textAlign": "center"},
                    ),
                    html.Img(
                        id="right-image",
                        src="",
                        style={
                            "width": "300px",
                            "display": "block",
                            "marginLeft": "auto",
                            "marginRight": "auto",
                        },
                    ),
                ],
                width=5,
                style={"textAlign": "center"},
            ),
        ],
    ),
    dbc.Row(
        [
            dbc.Label(
                "Table for selected/hovered patient with raw data",
                style={
                    "textAlign": "center",
                    "fontWeight": "bold",
                },
            ),
            dbc.Col(
                [
                    dash_table.DataTable(
                        id="table-patient-data",
                        style_table={"overflowX": "scroll"},
                    ),
                ]
            ),
        ],
        style={
            "marginTop": "10px",
            "marginBottom": "10px",
        },
    ),
]
