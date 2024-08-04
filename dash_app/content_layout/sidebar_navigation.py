import dash_bootstrap_components as dbc
from dash import dcc, html

from content_layout.offcanvas_3d_bundle_menu import offcanvas_3D_bundle_visualization
from content_layout.offcanvas_patient_selector_menu import offcanvas_patient_selector

sidebar_layout = (
    html.Div(
        [
            dcc.Loading(
                id="loading",
                type="circle",
                fullscreen=True,
                children=[
                    html.Div(
                        [
                            dcc.Upload(
                                id="upload-data",
                                children=dbc.Button(
                                    "Upload Patient Data",
                                    style={
                                        "textAlign": "center",
                                        "margin": "10px",
                                        "marginTop": "24px",
                                        "width": "100%",
                                    },
                                ),
                                # Allow multiple files to be uploaded
                                multiple=False,
                            )
                        ]
                    )
                ],
            ),
            dbc.Button(
                "Open Patient Selector",
                id="open-offcanvas-patient-selector",
                n_clicks=0,
                style={
                    "textAlign": "center",
                    "margin": "10px",
                    "width": "100%",
                },
            ),
            offcanvas_patient_selector,
            dbc.Button(
                "Open 3D Options",
                id="open-offcanvas-3D-bundle-visualization",
                n_clicks=0,
                style={
                    "textAlign": "center",
                    "margin": "10px",
                    "width": "100%",
                },
            ),
            dcc.Store(id="added-points-store"),
            dcc.Store(id="load-images-switch-prev"),
            dcc.Store(id="original-plot-x-y-axis"),
            offcanvas_3D_bundle_visualization,
            dcc.Loading(
                id="loading-2",
                type="circle",
                fullscreen=False,
                children=[
                    dbc.Switch(
                        id="load-images-switch",
                        value=False,
                        label="Load Image Markers",
                        style={
                            "margin": "10px",
                            "marginBottom": "0px",
                        },
                    ),
                    dbc.Label(
                        "Load Image Markers on the 2D plot. Changing the axis will reload the images.",
                        style={
                            "margin": "10px",
                        },
                        class_name="text-jusify",
                    ),
                    dcc.Store(id="pca-data-store"),
                    dcc.Store(id="pca-outlier-store"),
                    dcc.Store(id="patient-list-store"),
                    dcc.Store(id="hover-data-store"),
                ],
            ),
            dbc.Container(
                id="image_loading_container",
                children=[
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Spinner(id="progress_spinner"),
                                width=3,
                            ),
                            dbc.Col(
                                dbc.Label(
                                    "This might take a while... (~2 seconds per 200 images)"
                                ),
                                width=9,
                            ),
                        ]
                    ),
                ],
            ),
        ],
    ),
)
