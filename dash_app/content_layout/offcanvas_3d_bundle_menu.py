from dash import (
    html,
)
import dash_daq as daq
import dash_bootstrap_components as dbc

offcanvas_3D_bundle_visualization = dbc.Offcanvas(
    html.Div(
        [
            dbc.Label(
                "Select the mode for 3D Bundle Visualization",
                style={"font-weight": "bold"},
            ),
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dbc.Label(
                                "Each consecutive pair of points in a streamline is analyzed and colored based on its direction difference. This approach highlights the directional changes within each segment of the streamline, making it easier to visualize local variations in direction and curvature, particularly useful in detailed anatomical studies."
                            ),
                        ],
                        title="Segment-Based Coloring",
                    ),
                    dbc.AccordionItem(
                        [
                            dbc.Label(
                                "This method provides a simplified and clear visualization of the overall path and direction of each streamline, suitable for understanding the general orientation and trajectory of neural pathways across the brain."
                            ),
                        ],
                        title="Whole-Streamline Coloring",
                    ),
                ],
                style={"marginBottom": "10px"},
            ),
            dbc.RadioItems(
                id="coloring-mode",
                options=[
                    {
                        "label": "Segment-Based",
                        "value": "segment",
                    },
                    {
                        "label": "Whole-Streamline",
                        "value": "whole",
                    },
                ],
                value="segment",  # Default value
                labelStyle={"display": "block"},
            ),
            html.Hr(),
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dbc.Label(
                                "Applies cubic spline interpolation to smooth streamlines, especially beneficial for those with fewer points, defaulting to 50 segments per streamline."
                            )
                        ],
                        title="Cubic Spline Interpolation",
                    ),
                ],
                style={"marginBottom": "10px"},
            ),
            dbc.Switch(
                id="cubic-spline-selector",
                value=False,
                label="Apply cubic spline interpolation",
            ),
            dbc.Label("Number of Spline Points"),
            dbc.Input(
                id="num-spline-points",
                type="number",
                min=10,
                value=50,
                style={
                    "textAlign": "center",
                    "width": "100%",
                },
            ),
            html.Hr(),
            daq.ColorPicker(
                id="3d-background-color-picker",
                label="Background Color Picker",
                value=dict(hex="#000000"),
            ),
            html.Hr(),
            dbc.Button(
                "Show 3D Bundle for selected point",
                id="show-3D-bundle-for-selected-point",
                n_clicks=0,
                style={
                    "textAlign": "center",
                    "width": "100%",
                    "marginBottom": "10px",
                },
            ),
        ]
    ),
    id="offcanvas-3D-bundle-visualization",
    title="3D Bundle Visualization",
    is_open=False,
)
